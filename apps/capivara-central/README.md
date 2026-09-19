# COS Dev Center (`capivara-central`) — Snout

App de onboarding em português do CapivaraOS **Snout** (GNOME). No primeiro boot,
liga em um clique os extras opcionais da estação de desenvolvimento.

- **UI:** GTK4/libadwaita (nativa do GNOME). É o port da versão QML/Kirigami do
  Marsh (PROD-117) — mesmos cards e fluxo, toolkit do GNOME.
- **Backend:** `backend.py` (PyGObject/`Gio.Subprocess`). Orquestra os helpers
  em `libexec/`; a parte que precisa de root é elevada por `pkexec` DENTRO do
  helper (polkit `org.capivaraos.central.*`). O app nunca roda como root.
- **Entrada:** launcher `capivara-central` (usa `/usr/bin/python3`, NÃO o do PATH
  — ver BUG-44) → `capivara-central.py` (Adw.Application).

## Cards
IA local (Ollama + Alpaca + Continue), Trilhas de linguagem (mise), Ligar GPU
(ROCm/CUDA), Ferramentas de dev (VS Code/Cline/Open WebUI/Docker CE), GitHub CLI
+ pre-commit, e "Atualizar o CapivaraOS" (via `capivaraos-upgrade`, PROD-116;
aparece só quando há versão nova).

## Build
`./rpm/build-rpm.sh` → `~/rpmbuild/RPMS/noarch/capivara-central-*.snout.rpm`.
O `build-all.sh` da raiz constrói branding + central e monta a ISO.
