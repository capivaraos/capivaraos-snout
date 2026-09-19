# SPDX-License-Identifier: GPL-3.0-or-later
# Backend do COS Dev Center (CapivaraOS Snout, GNOME/GTK).
#
# Porta do backend do Marsh (que era PySide6/QProcess) para PyGObject: mesma
# lógica de instalação/estado, mas a plumbing de processo usa Gio.Subprocess e
# os avisos à UI são sinais GObject. Cada ação roda um script orquestrador (em
# /usr/libexec/capivara-central) via bash; a parte que precisa de root é elevada
# por pkexec DENTRO do script (polkit), então o app nunca roda como root.

import os
import re
import shutil
import subprocess

import gi
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gio, GLib, GObject  # noqa: E402

# App-id do Alpaca no Flathub (interface gráfica da IA local).
ALPACA_APP_ID = "com.jeffser.Alpaca"

# Trilhas de linguagem suportadas (ids de ferramenta do mise).
LANG_TRACKS = ("node", "python", "go", "rust", "java")

# Itens do card "Ferramentas de dev".
DEV_TOOLS = ("vscode", "cline", "openwebui", "docker")

# Ferramenta de upgrade de versão in-place (PROD-116). O card "Atualizar o
# CapivaraOS" só aparece quando ela está instalada — sem dependência RPM rígida,
# para não puxar o repo de updates para a ISO antes de o repo existir.
UPGRADE_TOOL = "capivaraos-upgrade"

# Diretório dos helpers. Em produção é /usr/libexec/capivara-central (instalado
# pelo RPM); em desenvolvimento cai para a pasta libexec/ ao lado deste arquivo.
_HERE = os.path.dirname(os.path.abspath(__file__))
LIBEXEC_DIRS = [
    "/usr/libexec/capivara-central",
    os.path.join(_HERE, "libexec"),
]


def _helper(name: str) -> str:
    for d in LIBEXEC_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    # Último recurso: nome cru (deixa o subprocess falhar com erro claro).
    return name


def _spawn_detached(argv) -> bool:
    """Inicia um processo desanexado (não bloqueia a UI, não captura saída)."""
    try:
        flags = (Gio.SubprocessFlags.STDOUT_SILENCE
                 | Gio.SubprocessFlags.STDERR_SILENCE)
        Gio.Subprocess.new(argv, flags)
        return True
    except GLib.Error:
        return False


class Backend(GObject.Object):
    """Ponte UI <-> sistema. Uma ação de cada vez (busy)."""

    __gsignals__ = {
        # uma linha de saída do processo
        "log-line": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        # rótulo do passo atual (pt-BR)
        "step-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        # ocupado? (para desabilitar botões)
        "busy-changed": (GObject.SignalFlags.RUN_FIRST, None, (bool,)),
        # (sucesso, mensagem)
        "finished": (GObject.SignalFlags.RUN_FIRST, None, (bool, str)),
        # (upgrade disponível?, versão de destino, pronto para reiniciar/aplicar?)
        "upgrade-status": (GObject.SignalFlags.RUN_FIRST, None, (bool, str, bool)),
    }

    def __init__(self):
        super().__init__()
        self._busy = False
        self._proc = None            # Gio.Subprocess em andamento
        self._stream = None          # Gio.DataInputStream do stdout
        self._action = ""            # rótulo da tarefa atual (p/ _finish)
        self._upgrade_target = ""    # versão Fedora de destino detectada
        self._upgrade_ready = False  # download já concluído nesta sessão

    # ---- Estado busy -----------------------------------------------------
    @property
    def busy(self) -> bool:
        return self._busy

    def _set_busy(self, value: bool):
        if self._busy != value:
            self._busy = value
            self.emit("busy-changed", value)

    # ---- Ações -----------------------------------------------------------
    def install_ai_local(self):
        """Instala o pacote de IA local: Ollama + Alpaca + extensão Continue."""
        self._run(_helper("setup-ai"), step="Preparando instalação da IA local…")

    def open_ai_local(self):
        """Abre o Alpaca (interface gráfica da IA local), sem caçar no menu."""
        if not _spawn_detached(["flatpak", "run", ALPACA_APP_ID]):
            _spawn_detached(["gtk-launch", ALPACA_APP_ID])

    def install_lang_tracks(self, langs):
        """Instala trilhas de linguagem via mise (por usuário, sem root)."""
        picks = [str(x) for x in langs if str(x) in LANG_TRACKS]
        if not picks:
            self.emit("log-line", "Nenhuma linguagem selecionada.")
            self.emit("finished", False, "Nenhuma linguagem selecionada.")
            return
        self._run(_helper("setup-langs"),
                  step="Preparando trilhas de linguagem…", args=picks)

    def enable_gpu(self):
        """Liga a aceleração por GPU (ROCm/AMD ou CUDA/NVIDIA) para o Ollama."""
        self._run(_helper("setup-gpu"), step="Preparando a ativação da GPU…")

    def install_dev_tools(self, tools):
        """Instala ferramentas de dev (VS Code/Cline/Open WebUI/Docker CE)."""
        picks = [str(x) for x in tools if str(x) in DEV_TOOLS]
        if not picks:
            self.emit("log-line", "Nenhuma ferramenta selecionada.")
            self.emit("finished", False, "Nenhuma ferramenta selecionada.")
            return
        self._run(_helper("setup-devtools"),
                  step="Preparando ferramentas de dev…", args=picks)

    def setup_gh(self):
        """Instala/configura gh + pre-commit (template global de hooks)."""
        self._run(_helper("setup-gh"), step="Configurando gh + pre-commit…")

    def open_gh_login(self):
        """Abre um terminal para o login interativo no GitHub (gh auth login).
        No Snout (GNOME) o terminal padrão é o Ptyxis; caímos para o
        gnome-terminal/xterm se necessário."""
        for term, args in (
            ("ptyxis", ["--", "gh", "auth", "login"]),
            ("gnome-terminal", ["--", "gh", "auth", "login"]),
            ("xterm", ["-e", "gh", "auth", "login"]),
        ):
            if shutil.which(term) and _spawn_detached([term] + args):
                return
        _spawn_detached(["gh", "auth", "login"])

    def open_app(self, kind: str):
        """Abre um app instalado a partir da seção 'Instalados' do catálogo."""
        if kind == "alpaca":
            self.open_ai_local()
        elif kind == "vscode":
            _spawn_detached(["code"])
        elif kind == "openwebui":
            # Garante o container de pé antes de abrir o navegador.
            try:
                subprocess.run(["podman", "start", "open-webui"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=15)
            except (OSError, subprocess.SubprocessError):
                pass
            _spawn_detached(["xdg-open", "http://localhost:3000"])
        elif kind == "gh":
            self.open_gh_login()
        # docker e lang:* não são "abríveis" (daemon / runtimes).

    # ---- Atualização de versão do CapivaraOS -----------------------------
    def check_upgrade(self):
        """Sonda, sem bloquear a UI, se há uma nova versão do CapivaraOS. Só faz
        sentido se a ferramenta capivaraos-upgrade estiver instalada; senão o
        card fica escondido. `capivaraos-upgrade check` é read-only."""
        if shutil.which(UPGRADE_TOOL) is None:
            self.emit("upgrade-status", False, "", False)
            return
        try:
            probe = Gio.Subprocess.new(
                [UPGRADE_TOOL, "check"],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_MERGE,
            )
        except GLib.Error:
            self.emit("upgrade-status", False, "", False)
            return
        probe.communicate_utf8_async(None, None, self._on_probe_done)

    def _on_probe_done(self, probe, res):
        try:
            _ok, out, _err = probe.communicate_utf8_finish(res)
        except GLib.Error:
            self.emit("upgrade-status", False, "", False)
            return
        target = ""
        for line in (out or "").splitlines():
            if "destino" in line:
                m = re.search(r"(\d+)", line)
                if m:
                    target = m.group(1)
        self._upgrade_target = target
        # Disponível quando o pré-voo aprova (exit 0: repo assinado do destino
        # existe). ready só vira True após um download nesta sessão.
        self.emit("upgrade-status", probe.get_successful(), target,
                  self._upgrade_ready)

    def download_upgrade(self):
        """Baixa a transação de upgrade (privilegiado; snapshot + dnf5
        system-upgrade download). Não reinicia."""
        self._run(_helper("setup-upgrade"),
                  step="Baixando a atualização do CapivaraOS…",
                  args=["download"], kind="upgrade-download")

    def reboot_upgrade(self):
        """Aplica: reinicia no modo offline. Passo terminal — a máquina reinicia."""
        self._run(_helper("setup-upgrade"),
                  step="Reiniciando para aplicar a atualização…",
                  args=["reboot"], kind="upgrade-reboot")

    # ---- Execução com streaming ------------------------------------------
    def _run(self, program: str, step: str = "", args=None, kind: str = ""):
        if self._busy:
            self.emit("log-line", "Já há uma tarefa em andamento; aguarde terminar.")
            return
        self._action = kind
        if step:
            self.emit("step-changed", step)
        self._set_busy(True)

        args = list(args or [])
        try:
            proc = Gio.Subprocess.new(
                ["/bin/bash", program] + args,
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_MERGE,
            )
        except GLib.Error as e:
            self.emit("log-line", f"Erro ao iniciar o processo ({e.message}).")
            self._set_busy(False)
            self.emit("finished", False, "Não foi possível iniciar a operação.")
            return
        self._proc = proc
        self.emit("log-line",
                  f"$ {os.path.basename(program)} {' '.join(args)}".rstrip())
        self._stream = Gio.DataInputStream.new(proc.get_stdout_pipe())
        self._read_line()

    def _read_line(self):
        self._stream.read_line_async(GLib.PRIORITY_DEFAULT, None, self._on_line)

    def _on_line(self, stream, res):
        try:
            line, _length = stream.read_line_finish_utf8(res)
        except GLib.Error:
            line = None
        if line is None:
            # EOF: todo o stdout foi consumido. Agora aguarda o processo sair
            # (para ter o status) e finaliza.
            if self._proc is not None:
                self._proc.wait_async(None, self._on_wait_done)
            return
        if line.startswith(">>> "):
            self.emit("step-changed", line[4:].strip())
        self.emit("log-line", line)
        self._read_line()

    def _on_wait_done(self, proc, res):
        try:
            proc.wait_finish(res)
            ok = proc.get_successful()
        except GLib.Error:
            ok = False
        self._finish(0 if ok else 1)

    def _finish(self, code: int):
        self._set_busy(False)
        self._proc = None
        self._stream = None
        action = self._action
        self._action = ""
        if code == 0:
            self.emit("step-changed", "Concluído!")
            if action == "upgrade-download":
                self._upgrade_ready = True
                self.emit("finished", True,
                          "Download da atualização concluído. Reinicie para aplicar.")
                self.emit("upgrade-status", True, self._upgrade_target, True)
            else:
                self.emit("finished", True, "Instalação concluída com sucesso.")
        else:
            self.emit("step-changed", "Falhou")
            self.emit("finished", False,
                      f"A operação terminou com erro (código {code}).")

    # ---- Consultas de estado (para os cards) -----------------------------
    def is_ai_local_installed(self) -> bool:
        """True só quando o pacote está completo: Ollama (motor) E Alpaca."""
        return shutil.which("ollama") is not None and self._alpaca_installed()

    @staticmethod
    def _alpaca_installed() -> bool:
        try:
            r = subprocess.run(
                ["flatpak", "info", "--system", ALPACA_APP_ID],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10,
            )
            return r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def is_gpu_enabled(self) -> bool:
        return (shutil.which("nvidia-smi") is not None
                or shutil.which("rocminfo") is not None)

    def is_gh_ready(self) -> bool:
        return shutil.which("gh") is not None

    @staticmethod
    def _lang_installed(lang: str) -> bool:
        base = os.path.expanduser(f"~/.local/share/mise/installs/{lang}")
        try:
            return os.path.isdir(base) and bool(os.listdir(base))
        except OSError:
            return False

    @staticmethod
    def _openwebui_present() -> bool:
        try:
            r = subprocess.run(
                ["podman", "ps", "-a", "--format", "{{.Names}}",
                 "--filter", "name=^open-webui$"],
                capture_output=True, text=True, timeout=10,
            )
            return "open-webui" in r.stdout
        except (OSError, subprocess.SubprocessError):
            return False

    @staticmethod
    def _cline_installed() -> bool:
        for d in ("~/.vscode-oss/extensions", "~/.vscode/extensions"):
            p = os.path.expanduser(d)
            try:
                if os.path.isdir(p):
                    for name in os.listdir(p):
                        if name.startswith("saoudrizwan.claude-dev"):
                            return True
            except OSError:
                pass
        return False

    def installed_apps(self):
        """Apps/itens instalados pelo Dev Center, para a faixa 'Instalados'.
        Cada item: {kind, name, icon, launch}."""
        apps = []
        if self._alpaca_installed():
            apps.append({"kind": "alpaca", "name": "Alpaca",
                         "icon": "com.jeffser.Alpaca", "launch": True})
        if shutil.which("code"):
            apps.append({"kind": "vscode", "name": "VS Code",
                         "icon": "code", "launch": True})
        if self._openwebui_present():
            apps.append({"kind": "openwebui", "name": "Open WebUI",
                         "icon": "web-browser-symbolic", "launch": True})
        if shutil.which("gh"):
            apps.append({"kind": "gh", "name": "GitHub CLI",
                         "icon": "git-symbolic", "launch": True})
        if shutil.which("docker"):
            apps.append({"kind": "docker", "name": "Docker",
                         "icon": "application-x-executable-symbolic", "launch": False})
        for lang in LANG_TRACKS:
            if self._lang_installed(lang):
                apps.append({"kind": "lang:" + lang, "name": lang.capitalize(),
                             "icon": "media-playlist-shuffle-symbolic", "launch": False})
        return apps

    def installed_langs(self) -> str:
        got = [l.capitalize() for l in LANG_TRACKS if self._lang_installed(l)]
        return ", ".join(got)

    def installed_lang_keys(self):
        """Chaves das trilhas já instaladas (p/ pré-marcar na folha de seleção)."""
        return [l for l in LANG_TRACKS if self._lang_installed(l)]

    def installed_tool_keys(self):
        """Chaves das ferramentas de dev já instaladas (p/ pré-marcar)."""
        got = []
        if shutil.which("code"):
            got.append("vscode")
        if self._cline_installed():
            got.append("cline")
        if self._openwebui_present():
            got.append("openwebui")
        if shutil.which("docker"):
            got.append("docker")
        return got

    def installed_dev_tools(self) -> str:
        got = []
        if shutil.which("code"):
            got.append("VS Code")
        if self._cline_installed():
            got.append("Cline")
        if self._openwebui_present():
            got.append("Open WebUI")
        if shutil.which("docker"):
            got.append("Docker")
        return ", ".join(got)
