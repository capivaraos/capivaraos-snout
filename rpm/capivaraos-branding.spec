# capivaraos-branding — identidade visual do CapivaraOS Snout (Fedora, GNOME)
#
# Equivalente, para a spin GNOME, ao rpm/capivaraos-branding.spec da spin KDE
# (../capivaraos-marsh-fedora/rpm/capivaraos-branding.spec): wallpapers,
# ícones "Sobre o Sistema", tema Plymouth de boot, tela de login GDM,
# /etc/os-release, /etc/issue, avatar padrão.
#
# Diferenças principais em relação à versão KDE (GNOME padrão, sem tema de
# terceiros tipo WhiteSur, sem dock/layout estilo macOS — decisão explícita
# para o Snout):
#   - Sem pacotes de wallpaper "estilo Plasma" (metadata.json); o equivalente
#     GNOME é um único XML em /usr/share/gnome-background-properties/, que
#     registra todos os wallpapers no seletor de fundo do GNOME Settings.
#   - Tela de login: GDM, não SDDM. GDM não tem um "theme.conf.user" como o
#     SDDM/breeze — o wallpaper do greeter é controlado via perfil dconf
#     próprio do GDM (/etc/dconf/profile/gdm + /etc/dconf/db/gdm.d/), que é o
#     mecanismo padrão usado por distros para customizar o fundo do GDM.
#   - Wallpaper do usuário: em vez de um script de runtime (como o
#     capivaraos-set-wallpaper da spin KDE/Xfce), usamos um default dconf
#     system-wide (/etc/dconf/db/local.d/) — aplica-se a qualquer usuário
#     novo sem depender de autostart/timing, e o usuário pode trocar
#     livremente depois (não bloqueamos a chave).
#   - Sem layout de painéis estilo macOS: GNOME Shell padrão (decisão
#     explícita do CapivaraOS Snout, diferente da spin Marsh).

Name:           capivaraos-branding
Version:        2.0.0
# O sufixo ".snout" no Release NAO e cosmetico -- e o que impede colisao de
# NEVRA entre as spins. As tres (Marsh, Pup, Snout) constroem um pacote com
# este MESMO Name e usam o mesmo ~/rpmbuild, entao duas spins na mesma
# Version-Release produzem nomes de arquivo identicos. Ja aconteceu duas
# vezes: em junho o dnf instalou o RPM do Pup no lugar do Snout (Pup e Snout
# ambos em 1.0.0), e em 21/07 um build do Pup consumiu sources da Marsh
# (BUG-30). Com o sufixo, a colisao passa a ser impossivel por construcao,
# em vez de depender de escolher versoes livres na mao.
#
# Serie 2.x (Fedora 45): pre-releases no padrao Fedora
# "0.N.alphaN.<dist>.snout" (0.1.alpha1, 0.2.alpha2, ...). O
# "2.0.0-1.<dist>.snout" fica RESERVADO para o LANCAMENTO PUBLICO conjunto das
# 3 spins (ver PROD-61). NEVRA 2.0.0-0.1.alpha1 < 2.0.0-1, entao o dnf nunca
# atualiza "pra tras". Builds de dev saem rotulados "preview".
Release:        0.12.alpha12%{?dist}.snout
# Rotulo da pre-release usado no /etc/os-release, /etc/issue e /etc/issue.net
# ("alphaN"). Fica num macro unico para NAO esquecer de subir junto com o
# Release (o fastfetch/Sobre leem o os-release; se divergir do nome da ISO, o
# sistema se reporta com a alpha errada). Ao subir o Release, suba isto tambem.
%global cos_label alpha12
Summary:        Identidade visual, wallpapers e branding padrão do CapivaraOS Snout 2.0.0 (preview)

License:        GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  ImageMagick
# /usr/bin/convert ou /usr/bin/magick
Requires:       plymouth
Requires:       gdm
Requires:       dconf

# NOTA CapivaraOS: NÃO declaramos "Conflicts: fedora-logos" aqui. Diferente
# da spin KDE (onde sddm/plasma não dependem de fedora-logos), neste Fedora
# 44 o pacote gdm tem uma dependência real em fedora-logos (confirmado via
# "dnf repoquery --whatrequires fedora-logos" no ambiente de build) —
# conflitar com ele tornaria o próprio gdm não instalável. Convivemos com
# fedora-logos instalado (não usamos os arquivos dele em lugar nenhum) e
# sobrescrevemos o que importa (wallpaper, os-release, tema Plymouth) via
# dconf/posttrans, sem remover o pacote.

%description
Pacote de identidade visual do CapivaraOS Snout 2.0.0 (preview): wallpapers da
marca da série 2.x (os mesmos do Marsh 2.0), conjunto de ícones
"capivaraos-logo" e "capivaraos-full-logo", tema Plymouth de boot, tela de
login GDM, /etc/os-release, /etc/issue e wallpaper padrão do GNOME (via
dconf), com o GNOME Shell padrão (sem customizações de layout).

%prep
%setup -q

%build
set -e
CONVERT=convert
command -v convert >/dev/null 2>&1 || CONVERT=magick

# ── 1. Ícones hicolor "capivaraos-logo" (apenas a capivara, sem texto) ──────
# NOTA: tamanho 36 incluído além do conjunto padrão das outras spins -- é um
# dos tamanhos em que o pacote fedora-logos instala "fedora-logo-icon" (ver
# %post), então precisamos da nossa logo nesse mesmo tamanho para sobrescrevê-lo.
mkdir -p build/icons
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" icons/capivaraos-logo.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png"
done

# ── 2. Ícones hicolor "capivaraos-full-logo" (capivara + texto "CapivaraOS") ─
# Usado pelo GNOME Settings ("Sobre") via LOGO= em /etc/os-release, e como
# base para sobrescrever "fedora-logo-icon" (ver %post).
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" backgrounds/CapivaraOS_Logo.png -background none -gravity center \
        -extent 1536x1536 -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png"
done

# ── 2b. Ícone REDONDO navy "capivaraos-round-logo" (capivara branca + texto
# num círculo azul-escuro) ──────────────────────────────────────────────────
# É o que sobrescreve o "fedora-logo-icon" (logo da distro): aparece na tela de
# boas-vindas do gnome-initial-setup e como ícone da distro no dock. Fonte:
# icons/capivaraos-round-logo.png (já circular, cantos transparentes) -- só
# redimensiona.
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    "$CONVERT" icons/capivaraos-round-logo.png -background none \
        -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-round-logo.png"
done

# ── 3. Ícone branco para a área de trabalho ("Instalar CapivaraOS" etc) ─────
mkdir -p build/pixmaps
"$CONVERT" icons/capivaraos-logo.png -fill white -colorize 100% \
    -resize 256x256 build/pixmaps/capivaraos-white.png

# ── 4. Avatar padrão (.face): a logo REDONDA navy (capivara branca + texto num
# círculo azul-escuro). O GNOME exibe o avatar recortado em círculo, então a
# logo redonda encaixa direto. Fonte: icons/capivaraos-round-logo.png (já
# circular, cantos transparentes). Antes era a capivara marrom sobre branco
# (trocado 2026-09-29 a pedido do dono, junto da revisão de cores).
"$CONVERT" icons/capivaraos-round-logo.png \
    -resize 256x256 build/pixmaps/capivaraos-face.png

# ── 4b. Logo quadrada (capivara, sem texto, fundo transparente) para o
# branding do Cockpit/Anaconda WebUI (instalador gráfico da ISO live) ───────
# Ver justificativa detalhada no spec da spin Pup. Em resumo: a cabeça é um
# asset versionado (icons/capivaraos-head.png), e não um -crop com
# coordenadas fixas sobre a logo-mestre -- as coordenadas antigas foram
# calibradas para a logo da capivara sentada e, com a logo nova (capivara
# andando), recortavam o lombo do animal sem falhar o build.
mkdir -p build/cockpit
"$CONVERT" icons/capivaraos-head.png \
    -resize 256x256 build/cockpit/logo.png
"$CONVERT" build/cockpit/logo.png -resize 32x32 build/cockpit/favicon.ico

# ── 5b. Logo 192x192 para substituir os pixmaps hardcoded do gnome-control-center
# O painel "Sistema" (Sobre) do gnome-control-center no Fedora 44 carrega o
# logo a partir de caminhos FIXOS no código (cc-info-entry.c), independente
# do campo LOGO= no os-release: /usr/share/pixmaps/fedora_logo_med.png (cor)
# e fedora_whitelogo_med.png (branco). Os originais Fedora eram 279x80 px;
# geramos em 192x192 (tamanho máximo do AdwClamp no painel Sobre) para que
# a logo apareça em tela cheia no painel, mais que dobrando o tamanho visual.
# Aparamos a margem transparente da logo-mestre ANTES do resize: assim ela
# ocupa quase todo o quadrado sem precisar do flag ^ (que preenche cortando
# as bordas). Com a logo da capivara andando -- mais larga que a antiga, da
# capivara sentada -- o ^ cortava a ponta do focinho, a pata traseira e as
# laterais do texto "CapivaraOS".
mkdir -p build/pixmaps-med
"$CONVERT" backgrounds/CapivaraOS_Logo.png -background none \
    -trim +repage -resize 192x192 -gravity center -extent 192x192 \
    build/pixmaps-med/capivaraos-logo-med.png
"$CONVERT" build/pixmaps-med/capivaraos-logo-med.png \
    -fill white -colorize 100% \
    build/pixmaps-med/capivaraos-whitelogo-med.png

# ── 5. Logo BRANCA para o splash do Plymouth (boot/desligamento) ────────────
mkdir -p build/plymouth
"$CONVERT" backgrounds/CapivaraOS_Logo.png -fill white -colorize 100% \
    -resize 320x320 build/plymouth/logo.png

# Spinner branco (arco girando) exibido logo abaixo da logo no splash.
mkdir -p build/plymouth/spinner
"$CONVERT" -size 64x64 xc:none -stroke white -strokewidth 5 \
    -fill none -draw "stroke-linecap round arc 12,12 52,52 0,300" \
    build/plymouth/spinner-base.png
for i in $(seq 0 29); do
    ANG=$(( i * 12 ))
    "$CONVERT" build/plymouth/spinner-base.png -background none \
        -distort SRT ${ANG} +repage "build/plymouth/spinner/${i}.png"
done

%install
set -e
# Wallpaper padrao do Snout 2.x: "Snout do Ano" (capivaraos-wp-snout-year),
# EXCLUSIVO do Snout (medalha "Snout of the Year" + logo branca no canto inferior
# DIREITO, mesma posicao/altura/formato dos demais, com sombra leve p/ ler no fundo
# claro). Os outros wp da marca (Luar, etc.)
# seguem disponiveis no seletor como opcao.
DEFAULT_WP=%{_datadir}/backgrounds/capivaraos/capivaraos-wp-snout-year.png

# ── Wallpapers ───────────────────────────────────────────────────────────────
# Serie 2.x: so os 8 wallpapers da marca (capivaraos-wp-*.png, os MESMOS do
# Marsh 2.0). O conjunto do Snout 1.x (fotos CC BY-SA + variantes de cor) foi
# removido; os wallpapers "padrao" continuam vindo do gnome-backgrounds da base.
# CapivaraOS_Logo.png fica na pasta so como FONTE de pixmaps/plymouth (nao e
# papel de parede), por isso e pulado aqui.
install -d %{buildroot}%{_datadir}/backgrounds/capivaraos
for WP in backgrounds/*.png; do
    [ "$(basename "$WP")" = "CapivaraOS_Logo.png" ] && continue
    install -m 0644 "$WP" %{buildroot}%{_datadir}/backgrounds/capivaraos/
done

# ── Pixmaps ──────────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/pixmaps
install -m 0644 icons/capivaraos.png %{buildroot}%{_datadir}/pixmaps/capivaraos.png
install -m 0644 icons/capivaraos-logo.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo.png
install -m 0644 build/pixmaps/capivaraos-white.png %{buildroot}%{_datadir}/pixmaps/capivaraos-white.png
install -m 0644 build/pixmaps-med/capivaraos-logo-med.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo-med.png
install -m 0644 build/pixmaps-med/capivaraos-whitelogo-med.png %{buildroot}%{_datadir}/pixmaps/capivaraos-whitelogo-med.png

# ── Icones hicolor ───────────────────────────────────────────────────────────
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-round-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
done

# ── Registro dos wallpapers no seletor de fundo do GNOME Settings ──────────
# Equivalente ao pacote de wallpaper KDE (metadata.json) da spin Marsh: um
# único XML em /usr/share/gnome-background-properties/ faz cada arquivo
# aparecer como opção no painel "Fundo" do GNOME Settings, com nome amigável
# (mesmo mecanismo usado pelo pacote gnome-backgrounds upstream).
install -d %{buildroot}%{_datadir}/gnome-background-properties
cat > %{buildroot}%{_datadir}/gnome-background-properties/capivaraos.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">
<wallpapers>
  <!-- Conjunto da marca da serie 2.x. "Snout do Ano" e o PADRAO (exclusivo Snout). -->
  <wallpaper deleted="false">
    <name>CapivaraOS Snout do Ano</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-snout-year.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Série 2</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-serie2.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Luar</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-moonlight.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Pôr do Sol</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-sunset.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Dev</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-dev.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Quadrinhos</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-comics.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Abstrato 1</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-abstract-1.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Abstrato 2</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-abstract-2.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Abstrato 3</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-abstract-3.png</filename>
    <options>zoom</options>
  </wallpaper>
  <wallpaper deleted="false">
    <name>CapivaraOS Abstrato 4</name>
    <filename>/usr/share/backgrounds/capivaraos/capivaraos-wp-abstract-4.png</filename>
    <options>zoom</options>
  </wallpaper>
</wallpapers>
EOF

# ── Tema Plymouth (idêntico às demais spins, ver justificativa no spec da
# Marsh: inclui a tela "Instalando atualizações" com percentual) ───────────
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos
install -m 0644 build/plymouth/logo.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/logo.png

install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner
install -m 0644 build/plymouth/spinner/*.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner/

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.plymouth << 'EOF'
[Plymouth Theme]
Name=CapivaraOS
Description=CapivaraOS boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/capivaraos
ScriptFile=/usr/share/plymouth/themes/capivaraos/capivaraos.script
EOF

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.script << 'EOF'
Window.SetBackgroundTopColor(0.07, 0.09, 0.13);
Window.SetBackgroundBottomColor(0.07, 0.09, 0.13);

# ── Logo branca (acima do spinner) ──────────────────────────────────────────
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.x = Window.GetWidth() / 2 - logo.image.GetWidth() / 2;
logo.y = Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 80;
logo.sprite.SetPosition(logo.x, logo.y, 1);

# ── Spinner (arco branco girando, logo abaixo da logo) ──────────────────────
spinner_frame_count = 30;
for (i = 0; i < spinner_frame_count; i++)
    spinner_image[i] = Image("spinner/" + i + ".png");

spinner.sprite = Sprite();
spinner.cx = Window.GetWidth() / 2;
spinner.cy = logo.y + logo.image.GetHeight() + 50;
spinner.frame = 0;

# ── Mensagem (abaixo do spinner) ────────────────────────────────────────────
# "updates"/"system-upgrade": modo usado pelo PackageKit/Software ao
# reiniciar para aplicar atualizacoes offline (systemd system-update.target).
is_updates = (Plymouth.GetMode() == "updates" || Plymouth.GetMode() == "system-upgrade");

if (Plymouth.GetMode() == "shutdown" || Plymouth.GetMode() == "reboot") {
    message_text = "Encerrando o CapivaraOS";
} else if (is_updates) {
    message_text = "Instalando atualizações";
} else {
    message_text = "Inicializando o CapivaraOS";
}

message.image = Image.Text(message_text, 1, 1, 1, 1, "Sans 14");
message.sprite = Sprite(message.image);
message.sprite.SetPosition(Window.GetWidth() / 2 - message.image.GetWidth() / 2,
                            spinner.cy + 70, 1);

# ── Aviso + percentual, somente durante atualizacao offline ────────────────
if (is_updates) {
    warning.image = Image.Text("Não desligue o computador", 0.8, 0.8, 0.8, 1, "Sans 11");
    warning.sprite = Sprite(warning.image);
    warning.sprite.SetPosition(Window.GetWidth() / 2 - warning.image.GetWidth() / 2,
                                spinner.cy + 95, 1);

    fun system_update_callback(progress) {
        percent.image = Image.Text(Math.Int(progress) + "%", 1, 1, 1, 1, "Sans 11");
        if (percent.sprite)
            percent.sprite.SetImage(percent.image);
        else
            percent.sprite = Sprite(percent.image);
        percent.sprite.SetPosition(Window.GetWidth() / 2 - percent.image.GetWidth() / 2,
                                    spinner.cy + 118, 1);
    }
    Plymouth.SetSystemUpdateFunction(system_update_callback);
}

fun refresh_callback() {
    spinner.frame++;
    if (spinner.frame >= spinner_frame_count * 3)
        spinner.frame = 0;
    idx = Math.Int(spinner.frame / 3);
    img = spinner_image[idx];
    spinner.sprite.SetImage(img);
    spinner.sprite.SetX(spinner.cx - img.GetWidth() / 2);
    spinner.sprite.SetY(spinner.cy - img.GetHeight() / 2);
}
Plymouth.SetRefreshFunction(refresh_callback);
EOF

# NOTA CapivaraOS: /etc/os-release/issue/issue.net NAO sao gerados aqui (em
# %{buildroot}). Pertencem a fedora-release-common; tê-los em %files causa
# conflito de arquivo no dnf. Escritos no sistema instalado em %posttrans.

# ── Avatar padrão (.face) para novos usuários ────────────────────────────────
install -d %{buildroot}%{_sysconfdir}/skel
install -m 0644 build/pixmaps/capivaraos-face.png %{buildroot}%{_sysconfdir}/skel/.face
ln -sf .face %{buildroot}%{_sysconfdir}/skel/.face.icon

# ── Branding do Cockpit (Anaconda WebUI) ────────────────────────────────────
install -d %{buildroot}%{_datadir}/cockpit/branding/capivaraos
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/logo.png
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/apple-touch-icon.png
install -m 0644 build/cockpit/favicon.ico %{buildroot}%{_datadir}/cockpit/branding/capivaraos/favicon.ico
cat > %{buildroot}%{_datadir}/cockpit/branding/capivaraos/branding.css << 'EOF'
/* SPDX-License-Identifier: LGPL-2.1-or-later */
#badge {
    inline-size: 225px;
    block-size: 80px;
    background-image: url("logo.png");
    background-size: contain;
    background-repeat: no-repeat;
}

#brand::before {
    content: "${NAME} <b>${VARIANT}</b>";
}

.anaconda {
    /* Paleta da marca CapivaraOS (verde) */
    --brand-default-light: #66bb6a;
    --brand-default: #2e7d32;
    --brand-default-dark: #1b5e20;

    .logo {
        background-image: url("logo.png");
        width: 2.5rem;
        height: 2.5rem;
    }
}

:not(.pf-v6-theme-dark) .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default);
    --pf-t--global--color--brand--hover: var(--brand-default-dark);
}

.pf-v6-theme-dark .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default-light);
    --pf-t--global--color--brand--hover: var(--brand-default);
}
EOF

# ── Decide de antemão o aviso de "repositórios de terceiros" do GNOME
# Software (fedora-third-party) ─────────────────────────────────────────────
# Sem isto, o diálogo "Habilitar repositórios de programas de terceiros?"
# reaparece para sempre na sessão live, mesmo clicando em "Ignorar" ou
# "Habilitar": ambos os botões disparam uma ação privilegiada via polkit
# (org.fedoraproject.thirdparty.run / .opt-out), que exige autenticação de
# admin -- e o "liveuser" da sessão live não tem senha definida para
# autenticar, então a ação falha silenciosamente e a decisão nunca é
# gravada em /var/lib/fedora-third-party/state.
#
# Em vez de tentar contornar isso com regras de polkit, pré-gravamos o
# estado já decidido como "não" -- coerente com a postura já adotada pelo
# CapivaraOS (ver PACKAGES.md da spin Marsh: "optamos por não habilitar RPM
# Fusion/repositórios de terceiros por padrão"). O arquivo não é
# %{_sysconfdir}/... mas sim /var/lib/ porque é onde o próprio
# fedora-third-party guarda esse estado (não é um arquivo de configuração
# do pacote fedora-third-party -- confirmado via "rpm -qf", ninguém é
# dono dele -- por isso podemos declará-lo nos %files deste pacote sem
# conflito). %config(noreplace): se o usuário mudar a escolha depois pelo
# GNOME Software (já autenticado normalmente, com senha real, no sistema
# instalado), uma atualização futura deste pacote não reverte a escolha.
install -d %{buildroot}%{_sharedstatedir}/fedora-third-party
cat > %{buildroot}%{_sharedstatedir}/fedora-third-party/state << 'EOF'
[main]
enabled = no
EOF

# ── Wallpaper padrão (system-wide, via dconf) ───────────────────────────────
# Mecanismo padrão do GNOME/dconf para definir um default que se aplica a
# qualquer usuário novo sem script de runtime: um keyfile em
# /etc/dconf/db/local.d/ + "dconf update" (feito em %posttrans) compilam o
# default na base binária /etc/dconf/db/local.d. Não bloqueamos a chave
# (sem locks/), então o usuário pode trocar livremente depois.
install -d %{buildroot}%{_sysconfdir}/dconf/db/local.d
cat > %{buildroot}%{_sysconfdir}/dconf/db/local.d/01-capivaraos-background << EOF
[org/gnome/desktop/background]
picture-uri='file://${DEFAULT_WP}'
picture-uri-dark='file://${DEFAULT_WP}'
picture-options='zoom'

[org/gnome/desktop/screensaver]
picture-uri='file://${DEFAULT_WP}'

EOF
# NOTA: NÃO definimos accent-color -- padronizamos na cor de destaque padrão do
# GNOME (azul). A marca CapivaraOS vem do wallpaper/logo, não de recolorir o
# accent do sistema (decisão 2026-09-29, alinhado ao que se fez no Marsh).

# ── Terminal fixado no dash (favorite-apps, system-wide via dconf) ───────────
# No GNOME stock o terminal (Ptyxis, o emulador padrao do Fedora) so aparece
# na grade de aplicativos; ao contrario do Xfce (Pup) e do KDE (Marsh), NAO
# fica no dash nem no botao-direito do desktop. Usuarios vindos das outras
# spins concluiam que "nao ha terminal". Adicionamos org.gnome.Ptyxis.desktop
# ao favorite-apps para o Terminal ficar visivel no dash. Mantemos os demais
# favoritos padrao do Fedora (setar a chave substitui a lista inteira, entao
# ela e reproduzida aqui). Nao bloqueamos a chave -- o usuario pode reordenar
# ou remover livremente.
cat > %{buildroot}%{_sysconfdir}/dconf/db/local.d/02-capivaraos-favorites << 'EOF'
[org/gnome/shell]
favorite-apps=['org.mozilla.firefox.desktop', 'org.gnome.Calendar.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Software.desktop', 'org.gnome.TextEditor.desktop', 'org.gnome.Calculator.desktop', 'org.gnome.Ptyxis.desktop']
EOF

# ── Wallpaper da tela de login (GDM) ─────────────────────────────────────────
# GDM roda sua própria sessão sob o usuário "gdm", que lê um perfil dconf
# PRÓPRIO (system-db:gdm), separado do perfil "user" usado por sessões
# normais. Sem isto, o greeter mostra o wallpaper padrão do Fedora/GNOME.
install -d %{buildroot}%{_sysconfdir}/dconf/profile
cat > %{buildroot}%{_sysconfdir}/dconf/profile/gdm << 'EOF'
user-db:user
system-db:gdm
file-db:/usr/share/gdm/greeter-dconf-defaults
EOF

install -d %{buildroot}%{_sysconfdir}/dconf/db/gdm.d
cat > %{buildroot}%{_sysconfdir}/dconf/db/gdm.d/01-capivaraos-background << EOF
[org/gnome/desktop/background]
picture-uri='file://${DEFAULT_WP}'
picture-uri-dark='file://${DEFAULT_WP}'
picture-options='zoom'

[org/gnome/login-screen]
# Logo do CapivaraOS (branca) no rodape da tela de login, no lugar da logo do
# Fedora. Nosso system-db:gdm tem prioridade sobre o file-db
# greeter-dconf-defaults (ver [[reference_gdm_greeter_dconf]]), entao esta chave
# sobrescreve a logo padrao do greeter.
logo='/usr/share/pixmaps/capivaraos-whitelogo-med.png'
EOF

# ── Perfil do Anaconda: faz o instalador reconhecer o CapivaraOS (BUG-38+BUG-42) ─
# O Anaconda casa o perfil de instalacao pelo os_id do /etc/os-release. Como o
# nosso ID e "capivaraos" (nao "fedora"), NENHUM perfil casava e o instalador
# caia no default de /etc/anaconda/anaconda.conf, que define efi_dir=default.
# Em UEFI isso faz o gen_grub_cfgstub tentar gravar o stub em
# /boot/efi/EFI/default (inexistente -- shim/grub2-efi instalam em /EFI/fedora)
# -> "gen_grub_cfgstub script failed" e a instalacao FALHA no passo do
# bootloader (BUG-38). So aparece em UEFI real; em VM no modo BIOS/legacy o
# caminho EFI nem roda (por isso nao pegamos antes). base_profile=fedora reusa
# efi_dir=fedora (BUG-38 resolvido) e MOSTRA a criacao de usuario no instalador
# (UserSpoke), que e o que queremos: o usuario e criado na instalacao.
#
# NOTA BUG-42 (o assistente-fantasma): NAO usar base_profile=fedora-workstation
# aqui. Tentamos (1.1.10) e NAO resolveu -- o problema real e OUTRO. O GDM, com
# daemon/InitialSetupEnable=true (default) e SEM o carimbo
# /var/lib/gnome-initial-setup/state, RELANCA a sessao do gnome-initial-setup a
# cada boot (roda como usuario dinamico do GDM, shell /sbin/nologin) em vez de
# logar a conta real -> nenhum terminal abre ("This account is currently not
# available.") e nao pede senha. Isso acontecia tanto com o usuario criado pelo
# instalador (perfil fedora) quanto pelo proprio assistente (perfil
# workstation). A correcao de verdade e DESLIGAR o assistente via
# InitialSetupEnable=false no %post (ver abaixo); como o instalador ja cria a
# conta, o assistente e desnecessario.
install -d %{buildroot}%{_sysconfdir}/anaconda/profile.d
cat > %{buildroot}%{_sysconfdir}/anaconda/profile.d/capivaraos.conf << 'EOF'
[Profile]
profile_id = capivaraos
base_profile = fedora

[Profile Detection]
os_id = capivaraos
EOF

# ── Snapshots pré-upgrade: config 'root' do snapper criada no 1o boot ────────
# O capivaraos-upgrade (PROD-116) só tira snapshot automático antes do upgrade
# in-place se a raiz for btrfs E existir uma config 'root' do snapper. O pacote
# snapper (ver %packages do kickstart) não cria essa config sozinho, e o
# instalador GNOME não a configura. Então um oneshot de 1o boot a cria no
# sistema INSTALADO (na live a raiz não é btrfs -> o script sai sem fazer nada).
# ConditionPathExists=!... faz o systemd pular o serviço depois de criada.
install -d %{buildroot}%{_libexecdir}/capivaraos
cat > %{buildroot}%{_libexecdir}/capivaraos/snapper-firstboot << 'EOF'
#!/bin/bash
# Cria a config 'root' do snapper se a raiz for btrfs e ainda não existir.
# Idempotente; pensado para rodar uma vez no 1o boot do sistema instalado.
set -e
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 0
command -v snapper >/dev/null 2>&1 || exit 0
snapper list-configs 2>/dev/null | grep -qw root && exit 0
snapper -c root create-config /
# Limites conservadores: sem timeline automática (não encher o disco); mantém
# os snapshots numerados (os pré/pós de transação e o do capivaraos-upgrade).
snapper -c root set-config TIMELINE_CREATE=no NUMBER_CLEANUP=yes NUMBER_LIMIT=10 NUMBER_LIMIT_IMPORTANT=10 || true
systemctl enable --now snapper-cleanup.timer >/dev/null 2>&1 || true
EOF
chmod 0755 %{buildroot}%{_libexecdir}/capivaraos/snapper-firstboot

install -d %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/capivaraos-snapper-setup.service << 'EOF'
[Unit]
Description=CapivaraOS: cria a configuracao snapper 'root' no 1o boot (btrfs)
Documentation=https://capivaraos.org
# Pula assim que a config existir (nada de stamp); e so em raiz btrfs.
ConditionPathExists=!/etc/snapper/configs/root
After=local-fs.target
Before=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/libexec/capivaraos/snapper-firstboot

[Install]
WantedBy=multi-user.target
EOF

# ── Logo próprio do fastfetch (FEAT-138 [Snout] / FEAT-50) ────────────────────
# O fastfetch mostra o logo ASCII do Fedora (escolhido por ID_LIKE do os-release).
# Trocamos pela cabeça de capivara da marca + "CapivaraOS" em verde. A arte vai
# em /usr/share/capivaraos/fastfetch/ e o config.jsonc (logo + a lista de módulos
# padrão -- um config só-logo imprimiria APENAS a capivara, sem as infos) em
# /etc/skel E /etc/xdg -- este ultimo p/ valer na sessao LIVE
# (fastfetch le XDG_CONFIG_DIRS=/etc/xdg). Sem auto-run (terminal limpo, decisão
# do dono): o logo só aparece ao rodar `fastfetch`. Portado do Marsh (FEAT-136).
install -d %{buildroot}%{_datadir}/capivaraos/fastfetch
install -m 0644 fastfetch/capivara.txt %{buildroot}%{_datadir}/capivaraos/fastfetch/capivara.txt
for FDIR in %{buildroot}%{_sysconfdir}/skel/.config %{buildroot}%{_sysconfdir}/xdg; do
    install -d "$FDIR/fastfetch"
    install -m 0644 fastfetch/config.jsonc "$FDIR/fastfetch/config.jsonc"
done

%post
# Splash de boot CapivaraOS
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# ── BUG-42: desliga o assistente de primeiro boot do GNOME (gnome-initial-setup)
# Sem isto, o GDM (daemon/InitialSetupEnable=true por default) RELANCA a sessao
# do gnome-initial-setup a cada boot -- ela roda como usuario dinamico do GDM,
# de shell /sbin/nologin -- em vez de logar a conta real do usuario. Efeito: o
# sistema "entra sozinho numa conta limitada tipo Live", nenhum terminal abre
# ("This account is currently not available.") e nao pede senha. O gatilho e a
# ausencia do carimbo /var/lib/gnome-initial-setup/state (que no nosso fluxo
# nunca e gravado). Como o usuario e criado pelo INSTALADOR (perfil fedora,
# UserSpoke visivel), o assistente e desnecessario: desligamos de vez.
#
# Escreve InitialSetupEnable=false na secao [daemon] do /etc/gdm/custom.conf,
# de forma idempotente e preservando as demais chaves (o gnome-control-center
# ainda pode ligar/desligar autologin depois; ele edita o keyfile sem apagar
# esta chave). Roda so no build (imagem live), mas o arquivo resultante e o que
# o instalador copia para o disco -- a sessao live sobrescreve o custom.conf via
# livesys (autologin=liveuser), sem efeito no que e instalado.
GDM_CONF=%{_sysconfdir}/gdm/custom.conf
if [ -f "$GDM_CONF" ]; then
    if grep -q '^\s*InitialSetupEnable\s*=' "$GDM_CONF"; then
        sed -ri 's/^\s*InitialSetupEnable\s*=.*/InitialSetupEnable=false/' "$GDM_CONF"
    elif grep -q '^\[daemon\]' "$GDM_CONF"; then
        sed -i '0,/^\[daemon\]/s//[daemon]\nInitialSetupEnable=false/' "$GDM_CONF"
    else
        printf '\n[daemon]\nInitialSetupEnable=false\n' >> "$GDM_CONF"
    fi
fi

# ── Sobrescreve o ícone "fedora-logo-icon" com a logo do CapivaraOS ────────
# A tela de boas-vindas da sessão live (gnome-initial-setup) e o painel
# "Sobre" do GNOME Settings NÃO lêem o LOGO= do /etc/os-release
# dinamicamente -- confirmado via "strings" no binário gnome-initial-setup:
# ele tem uma tabela FIXA, no código, de nomes de ícone por distro
# reconhecida ("fedora-logo-icon", "ubuntu-logo-icon", "opensuse-logo-icon"
# ...). Como "capivaraos" não está nessa tabela, cai no fallback Fedora.
# A correção (igual a outras distros baseadas em Fedora) é sobrescrever o
# CONTEÚDO do ícone "fedora-logo-icon" com a nossa logo, nos mesmos
# tamanhos em que o pacote fedora-logos o instala -- sem declarar esses
# caminhos em %files (evita conflito de arquivo no dnf, mesmo princípio
# usado para /etc/os-release).
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    SRC=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-round-logo.png
    DST=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/fedora-logo-icon.png
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done

# ── Sobrescreve logos hardcoded no gnome-control-center ───────────────────
# O painel "Sistema" (Sobre) do gnome-control-center no Fedora 44 usa caminhos
# FIXOS no código (cc-info-entry.c) para o logo da distro, independente do
# campo LOGO= do os-release. Os arquivos são do pacote fedora-logos:
# fedora_logo_med.png (279x80, colorido) e fedora_whitelogo_med.png (branco).
# Sobrescrevemos com nossa logo; sem declarar em %files (evita conflito com
# fedora-logos, mesmo padrão do fedora-logo-icon).
for PAIR in \
    "capivaraos-logo-med.png:fedora_logo_med.png" \
    "capivaraos-whitelogo-med.png:fedora_whitelogo_med.png"; do
    SRC=%{_datadir}/pixmaps/${PAIR%%:*}
    DST=%{_datadir}/pixmaps/${PAIR##*:}
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done

# GRUB_DISTRIBUTOR -> "CapivaraOS"
if [ -f %{_sysconfdir}/default/grub ]; then
    if grep -q '^GRUB_DISTRIBUTOR=' %{_sysconfdir}/default/grub; then
        sed -i 's/^GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="CapivaraOS"/' %{_sysconfdir}/default/grub
    else
        echo 'GRUB_DISTRIBUTOR="CapivaraOS"' >> %{_sysconfdir}/default/grub
    fi
fi

# Compila os keyfiles de /etc/dconf/db/*.d/ nas bases binarias lidas em
# tempo de execucao pelo gnome-shell/gdm.
dconf update >/dev/null 2>&1 || true

gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

%postun
if [ "$1" -eq 0 ]; then
    gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true
    dconf update >/dev/null 2>&1 || true
fi

%posttrans
# Tema padrao do Plymouth (boot/desligamento): ver justificativa detalhada
# no spec da spin Marsh (idêntica para esta spin).
install -d %{_sysconfdir}/plymouth
cat > %{_sysconfdir}/plymouth/plymouthd.conf << 'EOF'
[Daemon]
Theme=capivaraos
EOF
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# Habilita o oneshot que cria a config 'root' do snapper no 1o boot (PROD-116).
# %posttrans roda com systemd/snapper ja instalados; o enable offline apenas cria
# o symlink WantedBy — o servico so age no 1o boot do sistema instalado (btrfs).
systemctl enable capivaraos-snapper-setup.service >/dev/null 2>&1 || true

# /etc/os-release, /etc/issue, /etc/issue.net (fedora-release-common):
# escritos aqui (em vez de %files) para evitar conflito de arquivo no dnf.
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Snout 2.0.0 (%{cos_label}, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=45
VERSION_CODENAME=snout
PLATFORM_ID="platform:f45"
PRETTY_NAME="CapivaraOS Snout 2.0.0 (%{cos_label}, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-round-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:45"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=45
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=45
VARIANT="Snout 2.0.0 (%{cos_label}, preview)"
VARIANT_ID=snout
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Snout 2.0.0 (%{cos_label}, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Snout 2.0.0 (%{cos_label}, preview)
EOF

# ── Reaplica os-release apos qualquer atualizacao futura do sistema ────────
# Ver justificativa detalhada no spec da spin KDE (mesmo mecanismo: garante
# que o titulo GRUB/BLS de kernels novos nao volte a "Fedora Linux").
#
# ATENCAO -- NAO troque o prefixo abaixo por um caminho de arquivo exato
# (ex.: /etc/os-release). Verificado empiricamente em container fedora:44
# (2026-07-17, spin Marsh): o %transfiletriggerin casa APENAS com prefixos de
# DIRETORIO e NUNCA com caminhos de arquivo exatos. Ate a 1.0.8 este gatilho
# era "-- %{_sysconfdir}/os-release" -- codigo morto: nunca disparou uma
# unica vez, e o bug que ele deveria corrigir seguia acontecendo em silencio.
#
# Por isso vigiamos o diretorio /usr/lib (dirname do arquivo que importa:
# /usr/lib/os-release, que pertence ao fedora-release-identity-basic; o
# /etc/os-release e apenas um symlink para ele). Esse prefixo dispara em
# quase toda transacao, entao a guarda logo abaixo faz o caso comum sair de
# imediato; so pagamos o kernel-install quando o os-release foi revertido.
%transfiletriggerin -- %{_prefix}/lib
# Caso comum: nosso os-release intacto, nada a fazer.
grep -q '^NAME="CapivaraOS"' %{_prefix}/lib/os-release 2>/dev/null && exit 0
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Snout 2.0.0 (%{cos_label}, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=45
VERSION_CODENAME=snout
PLATFORM_ID="platform:f45"
PRETTY_NAME="CapivaraOS Snout 2.0.0 (%{cos_label}, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-round-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:45"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=45
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=45
VARIANT="Snout 2.0.0 (%{cos_label}, preview)"
VARIANT_ID=snout
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Snout 2.0.0 (%{cos_label}, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Snout 2.0.0 (%{cos_label}, preview)
EOF

for kver in $(ls /lib/modules 2>/dev/null); do
    [ -f "/lib/modules/${kver}/vmlinuz" ] && \
        kernel-install add "${kver}" "/lib/modules/${kver}/vmlinuz" >/dev/null 2>&1 || true
done

# ── Reaplica o ícone fedora-logo-icon após qualquer atualização futura ─────
# Mesmo mecanismo do file trigger de /etc/os-release: se uma atualização
# futura do fedora-logos reescrever algum desses arquivos, este trigger
# reaplica a nossa logo por cima.
#
# ATENÇÃO -- o prefixo abaixo é um DIRETÓRIO de propósito. Até a 1.0.8 este
# gatilho listava os 11 caminhos exatos dos fedora-logo-icon.png; como o
# %transfiletriggerin casa apenas com prefixos de diretório, ele era código
# morto e nunca reaplicou a logo uma única vez. Ver a nota longa no gatilho
# de os-release acima.
#
# /usr/share/icons/hicolor é mexido por muitos pacotes, então a guarda abaixo
# faz o caso comum (nossa logo já no lugar) sair de imediato.
%transfiletriggerin -- %{_datadir}/icons/hicolor
cmp -s %{_datadir}/icons/hicolor/48x48/apps/capivaraos-round-logo.png \
       %{_datadir}/icons/hicolor/48x48/apps/fedora-logo-icon.png && exit 0
for SIZE in 16 22 24 32 36 48 64 96 128 256 512; do
    SRC=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-round-logo.png
    DST=%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/fedora-logo-icon.png
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done
gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

# ── Reaplica o logo do gnome-control-center após atualização do fedora-logos ─
# Prefixo de DIRETÓRIO pelo mesmo motivo dos gatilhos acima: até a 1.0.8 aqui
# estavam os dois caminhos exatos de pixmap, e o gatilho nunca disparou.
%transfiletriggerin -- %{_datadir}/pixmaps
cmp -s %{_datadir}/pixmaps/capivaraos-logo-med.png \
       %{_datadir}/pixmaps/fedora_logo_med.png && exit 0
for PAIR in \
    "capivaraos-logo-med.png:fedora_logo_med.png" \
    "capivaraos-whitelogo-med.png:fedora_whitelogo_med.png"; do
    SRC=%{_datadir}/pixmaps/${PAIR%%:*}
    DST=%{_datadir}/pixmaps/${PAIR##*:}
    [ -f "$SRC" ] && [ -d "$(dirname "$DST")" ] && cp -f "$SRC" "$DST"
done

%files
%{_datadir}/backgrounds/capivaraos/
%{_datadir}/pixmaps/capivaraos.png
%{_datadir}/pixmaps/capivaraos-logo.png
%{_datadir}/pixmaps/capivaraos-white.png
%{_datadir}/pixmaps/capivaraos-logo-med.png
%{_datadir}/pixmaps/capivaraos-whitelogo-med.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-full-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-round-logo.png
%{_datadir}/gnome-background-properties/capivaraos.xml
%{_datadir}/plymouth/themes/capivaraos/
%{_datadir}/cockpit/branding/capivaraos/
%{_sysconfdir}/skel/.face
%{_sysconfdir}/skel/.face.icon
%config(noreplace) %{_sharedstatedir}/fedora-third-party/state
%config(noreplace) %{_sysconfdir}/dconf/db/local.d/01-capivaraos-background
%config(noreplace) %{_sysconfdir}/dconf/db/local.d/02-capivaraos-favorites
%config(noreplace) %{_sysconfdir}/dconf/profile/gdm
%config(noreplace) %{_sysconfdir}/dconf/db/gdm.d/01-capivaraos-background
%{_sysconfdir}/anaconda/profile.d/capivaraos.conf
%dir %{_datadir}/capivaraos
%{_datadir}/capivaraos/fastfetch/
%{_sysconfdir}/skel/.config/fastfetch/
%{_sysconfdir}/xdg/fastfetch/
%{_libexecdir}/capivaraos/snapper-firstboot
%{_unitdir}/capivaraos-snapper-setup.service

%changelog
* Tue Oct 13 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.12.alpha12
- Fastfetch: corrige o config.jsonc que mostrava SÓ o logo (a cabeça de capivara)
  sem nenhuma info do sistema. Ao passar um config próprio, o fastfetch não aplica
  a lista de módulos padrão sozinho — um config só-"logo" imprime apenas o logo.
  Adicionada a lista "modules" padrão ao config.jsonc; o logo/cor fica intocado.
  Provado no fastfetch 2.69. (reference_fastfetch_logo / aviso vindo do Herd.)
- os-release/issue: o rótulo da pré-release (VERSION/PRETTY_NAME/VARIANT/issue)
  estava preso em "alpha11" enquanto a ISO já era alpha12 — o fastfetch/Sobre
  reportavam a alpha errada. Corrigido para alpha12 e parametrizado num macro
  único (%%global cos_label) para não divergir do Release em bumps futuros.

* Fri Oct 09 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.11.alpha11
- Título do menu de boot (GRUB) agora acompanha a versão do CapivaraOS + Fedora:
  "CapivaraOS Snout 2 45" (2 = série do CapivaraOS, 45 = Fedora). Feito pelo lorax
  no COMPOSE via --project="CapivaraOS Snout 2" + @VERSION@ (releasever) no
  build-all.sh — mesmo approach do Pup. O retítulo pós-build via xorriso NÃO pega
  no F45 (foi removido). Antes era só "CapivaraOS Snout 45".
- Wallpaper "Snout do Ano": a logo do CapivaraOS foi movida do canto inferior
  esquerdo para o DIREITO (mesma posição dos demais wallpapers), com sombra leve
  ao redor para não sumir no fundo claro.

* Fri Oct 09 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.10.alpha10
- Novo wallpaper EXCLUSIVO do Snout: "Snout do Ano" (capivaraos-wp-snout-year.png,
  3840x2160) — medalha "Snout of the Year" + logo branca do CapivaraOS no canto
  inferior ESQUERDO (mesma altura/formato dos demais, com halo escuro suave p/ ler
  no fundo claro). Vira o wallpaper PADRAO do Snout (DEFAULT_WP) e entra no topo do
  seletor de fundo do GNOME; os demais (Luar, Série 2, etc.) seguem como opção.
  Metadados conferidos/limpos (-strip; sem EXIF/IPTC/XMP). So no Snout.

* Thu Oct 08 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.9.alpha9
- ISO passa a trazer pré-instalado o COS Config Center (cos-config 0.11.1), a
  central de configuração do CapivaraOS (PROD-141/PROD-5). O pacote NÃO é buildado
  aqui: vem já ASSINADO do repositório (repo.capivaraos.org/snout/f45/x86_64/<canal>,
  padrão testing) e o build-all.sh baixa, confere a assinatura (gpgcheck + chave do
  projeto) e só então inclui. Integração mesclada pelo PR #1 (commit 588a07e); este
  bump oficializa a ISO com o app. Só rótulo/versão da branding aqui.

* Tue Sep 29 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.8.alpha8
- Padroniza no visual padrão do GNOME (a pedido do dono): (1) remove o
  accent-color='green' do dconf -- o realce do sistema (foco, botões, polkit)
  volta ao AZUL padrão do GNOME; a marca vem do wallpaper/logo, não de recolorir
  o accent. (2) Avatar padrão (.face) deixa de ser a capivara MARROM sobre branco
  e passa a ser a logo REDONDA navy (capivaraos-round-logo). Instalador (Anaconda)
  e ANSI_COLOR do terminal seguem como estão (decisão: reverter só o accent).

* Tue Sep 29 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.7.alpha7
- BLOCKER de boot (PROD-133): remove o /etc/kernel/cmdline "fantasma" no %post do
  capivaraos-post-branding.ks (após o loop do dracut). O arquivo nascia no build da
  live com o UUID de raiz do build e sem rootflags=subvol=root; o liveimg o copiava
  pro alvo e o 1º update de kernel gerava uma BLS quebrada -> dracut emergency mode.
  Removido, o kernel-install deriva a cmdline do /proc/cmdline real do instalado
  (root+rootflags corretos p/ qualquer layout). Espelhado do Marsh (commit 0bbc113).

* Thu Sep 24 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.6.alpha6
- Logo redonda navy também no painel "Sobre" do GNOME: os-release LOGO= passa de
  capivaraos-full-logo para capivaraos-round-logo (o GNOME 49 do F45 usa o LOGO= do
  os-release no painel Sobre). NÃO mexe no capivaraos-whitelogo-med, que também é a
  logo da tela de login do GDM — o login segue com a logo branca.

* Thu Sep 24 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.5.alpha5
- Logo redonda navy nas telas da distro: a tela de boas-vindas (gnome-initial-setup)
  e o ícone da distro no dock passam a usar a nova logo REDONDA (capivara branca +
  "CapivaraOS" num círculo azul-escuro) no lugar da logo marrom. Fonte
  icons/capivaraos-round-logo.png (circular, cantos transparentes); gera os tamanhos
  hicolor "capivaraos-round-logo" e o override do fedora-logo-icon (%post +
  %transfiletriggerin) passa a copiá-la. O capivaraos-full-logo (os-release LOGO= /
  painel "Sobre") fica intacto. Também alinha o build-all.sh (estava em alpha3
  enquanto o branding já estava em alpha4).

* Thu Sep 24 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.4.alpha4
- Logo próprio do CapivaraOS no fastfetch (FEAT-138/FEAT-50): substitui o logo ASCII
  do Fedora pela capivara + "CapivaraOS" (verde #15B22C). Arte em
  /usr/share/capivaraos/fastfetch/capivara.txt + config.jsonc (só o logo) em
  /etc/skel/.config/fastfetch e /etc/xdg/fastfetch. Portado do Marsh (FEAT-136); sem
  auto-run (terminal limpo) — aparece ao rodar `fastfetch`.

* Mon Sep 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.3.alpha3
- Wallpaper novo da marca "Série 2" (capivaraos-wp-serie2.png, 3840x2160) — o hero
  verde da série 2, portado do Pup 2.x (fonte brand-assets/). Entra no seletor de
  fundo do GNOME junto dos demais; o padrão segue "Luar" (moonlight), como no Pup.

* Fri Sep 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.2.alpha2
- Snapshots "atualize sem medo" (PROD-116): o Snout 2.x passa a criar a config
  'root' do snapper no 1o boot (oneshot capivaraos-snapper-setup.service +
  /usr/libexec/capivaraos/snapper-firstboot), em raiz btrfs. Sem isso o
  capivaraos-upgrade nao tirava snapshot automatico antes do upgrade in-place
  (so instalar o pacote snapper, como o Marsh faz, nao basta — falta a config).
  Na sessao live e no-op (raiz nao e btrfs). Pacotes snapper + btrfs-assistant
  entram pelo %packages do kickstart. Falta validar em VM instalada.

* Fri Sep 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.1.alpha1
- Primeira build da serie 2.x do Snout: rebase para Fedora 45 (base do 2.0) — PROD-114.
  O F45 Beta saiu (2026-09-18). Repo novo capivaraos-snout-next (clonado do
  capivaraos-snout-fedora p/ preservar a base GNOME + o fix do BUG-42), branch
  rebase-f45. Repoint do compose: build-all.sh --releasever=45, base do kickstart
  f44 -> f45 (fedora-45/updates-released-f45), trava de updates em 45. os-release/
  issue -> Fedora 45 + "Snout 2.0.0 (%{cos_label}, preview)". Snout CONTINUA GNOME.
  Versionamento pre-release "0.N.alphaN.snout"; "2.0.0-1.snout" reservado p/ o
  lancamento publico conjunto das 3 spins (PROD-61). SMOKE BUILD p/ levantar
  quebras (GNOME/GDM no F45, Anaconda 45) — NAO cortar ISO publica do F45 antes do GA.
- Wallpapers da marca da serie 2.x (PROD-115): so os MESMOS 8 do Marsh 2.0 (Luar,
  Por do Sol, Dev, Quadrinhos, Abstrato 1-4), empacotados e registrados no seletor
  de fundo do GNOME; padrao passa a ser "Luar" (moonlight), igual ao Marsh. O
  conjunto proprio do Snout 1.x (7 fotos CC BY-SA do Wikimedia + variantes de cor +
  capivaraos-wallpaper.png) foi REMOVIDO do 2.x; os wallpapers "padrao" seguem vindo
  do gnome-backgrounds da base. Removidos tambem CREDITOS.txt (era das fotos) e os
  scripts regen-photo/solid-wallpapers.sh; tags CC-BY-SA saem da License.

* Sat Aug 22 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.15-1
- CORRIGE a tela de login (BUG-42): sem autologin, o GDM nao mostrava a tela de
  login -- entrava direto numa "sessao fantasma" (greeter quebrado, rodando como
  gdm-greeter) e so dava para acessar a conta ligando o inicio automatico de
  sessao. Causa: ao customizar o wallpaper do greeter nos sobrescrevemos o
  /etc/dconf/profile/gdm e deixamos de fora a 3a linha padrao do Fedora,
  "file-db:/usr/share/gdm/greeter-dconf-defaults", que carrega a configuracao da
  tela de login do GDM. Sem ela o greeter perde os defaults e nao renderiza o
  login. Fix: reincluir essa linha no perfil (as 3 linhas do padrao Fedora).
  Validado ao vivo: a tela de login volta, o usuario entra com a senha e o
  terminal funciona. (Versoes 1.1.10-1.1.14 foram iteracoes internas de
  diagnostico, nao publicadas.)
- Branding do greeter: logo do CapivaraOS (branca) no rodape da tela de login,
  no lugar da logo do Fedora -- via org.gnome.login-screen logo no db gdm.d
  (system-db:gdm tem prioridade sobre o greeter-dconf-defaults).
- Tambem nesta versao: perfil do Anaconda base_profile=fedora (instalador cria a
  conta; mantem efi_dir=fedora do BUG-38); InitialSetupEnable=false (nao roda o
  assistente de 1o boot, ja que a conta vem do instalador); Terminal fixado no
  dash (favorite-apps org.gnome.Ptyxis.desktop).

* Tue Aug 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.9-1
- Instala em UEFI real: adiciona /etc/anaconda/profile.d/capivaraos.conf com
  base_profile=fedora. Sem ele o Anaconda nao casava perfil (ID=capivaraos),
  caia em efi_dir=default e o gen_grub_cfgstub falhava no fim da instalacao em
  UEFI ("gen_grub_cfgstub script failed") -- BUG-38. So aparecia em UEFI real;
  VM em modo BIOS/legacy nao pegava. Herdar fedora reusa efi_dir=fedora.
- (kickstart) initramfs de build agora --no-hostonly --no-hostonly-cmdline: o
  sistema instalado passa a achar o disco raiz em hardware com storage diferente
  do build (BUG-40), em vez de cair em emergency mode ("Not all disks have been
  found").

* Fri Aug 14 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.6-2
- Reconciliacao de licenca/marca (LEG-4): corrige o metadado License: do RPM.
  Antes "CC-BY-SA-4.0 AND MIT" -- (a) marcava MIT sem nada MIT no pacote (codigo
  e config do projeto sao GPLv3, como o LICENSE de topo), (b) varria a identidade
  visual sob CC-BY-SA (contradiz a marca) e (c) omitia CC-BY-SA-3.0 de uma das
  fotos embarcadas. Agora: GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
  AND CC-BY-SA-3.0 AND CC-BY-SA-4.0. Correcao de metadado apenas; a atribuicao
  exigida (CREDITOS.txt + creditos gravados nas imagens) ja estava correta (LEG-3).
- Adiciona TRADEMARK.md: nome/logo CapivaraOS sao marca do projeto (direitos
  reservados); codigo GPLv3; wallpapers fotograficos de terceiros CC BY-SA
  creditados em backgrounds/CREDITOS.txt.

* Wed Aug 12 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.6-1
- Corrige a atribuicao das fotos de Giles Laurent nos wallpapers: a
  licenca CC BY-SA 4.0 do autor exige o texto verbatim "(c) Giles
  Laurent, gileslaurent.com, License CC BY-SA 4.0"; o credito gravado
  antes ("Foto: Giles Laurent - CC BY-SA 4.0") omitia o dominio
  gileslaurent.com exigido. Ajustadas as 3 fotos (ipe, natacao, salto)
  e o CREDITOS.txt. Ver LEG-3.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.5-1
- A arte-mestre backgrounds/CapivaraOS_Logo.png deixa de ser instalada como
  papel de parede. Ela mora na pasta backgrounds/ apenas por ser a FONTE dos
  wallpapers, mas o loop de instalacao a levava junto -- aparecia no seletor
  de fundo do GNOME como opcao escolhivel e, aplicada, saia desproporcional.
  Diagnosticado na spin Pup em 2026-07-21; as tres tinham o mesmo defeito.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.4-1
- Rebrand: nova logo do CapivaraOS (capivara andando) em todo o branding.
  A logo anterior (capivara sentada) era derivada de um desenho de banco de
  imagens e apresentava risco de similaridade substancial; a nova arte e
  original. Ver DOC-6.
  . backgrounds/CapivaraOS_Logo.png trocada pela arte nova (mesmo canvas
    1536x1024), e icons/capivaraos-logo.png pela capivara sem texto.
  . 7 wallpapers de cor solida, capivaraos-wallpaper.png e o icone quadrado
    icons/capivaraos.png regerados por branding/regen-solid-wallpapers.sh
    (script novo aqui, trazido da spin Marsh -- offline, nao precisa de rede).
  . 6 wallpapers fotograficos regerados por regen-photo-wallpapers.sh, para
    que a marca d'agua e os creditos saiam com a logo nova.
- Assets derivados deixam de sair de -crop com coordenadas fixas sobre a
  logo-mestre e passam a vir de arquivos versionados:
  . logo do Cockpit/Anaconda WebUI: agora icons/capivaraos-head.png (asset
    novo). O recorte antigo, "-crop 360x300+480+90", fora calibrado para a
    capivara sentada; com a logo nova ele recortava o LOMBO do animal, sem
    falhar o build.
  . avatar padrao (.face): agora icons/capivaraos-logo.png achatada sobre
    branco, no lugar de "-crop 1536x600+0+0".
- Logo do painel "Sobre" do gnome-control-center: aparamos a margem
  transparente antes do resize e trocamos "-resize 192x192^" por
  "-resize 192x192". O flag ^ preenche o quadrado CORTANDO as bordas; com a
  logo nova, mais larga, ele decepava a ponta do focinho, a pata traseira e
  as laterais do texto "CapivaraOS". Aparando antes, a logo sai inteira e
  praticamente do mesmo tamanho.
- Corrige TRES file triggers que eram codigo morto. Todos listavam caminhos
  de ARQUIVO exatos, e o %transfiletriggerin casa apenas com prefixos de
  DIRETORIO -- nenhum deles disparou uma unica vez desde que foi escrito:
  . os-release: "-- /etc/os-release" -> "-- /usr/lib" (mesma correcao da
    spin Marsh). Sem ele, uma atualizacao futura do fedora-release reverte o
    os-release e o titulo GRUB/BLS de kernels novos volta a "Fedora Linux".
  . fedora-logo-icon: os 11 caminhos hicolor -> "-- /usr/share/icons/hicolor".
  . pixmaps do gnome-control-center: os 2 caminhos -> "-- /usr/share/pixmaps".
  Os dois ultimos ganharam guarda com "cmp -s" para sair de imediato no caso
  comum, ja que esses diretorios sao tocados por muitos pacotes.

* Sat Jun 27 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.8-1
- Fotos de fundo geradas em 1920×1440 (4:3) com logo e créditos na zona
  segura (y=+240 do rodapé): visíveis em monitores 4:3 (encaixe perfeito,
  sem crop lateral) e 16:9 (o zoom recorta 180px do topo/rodapé, mas os
  elementos ficam a 60px acima do corte). Logo branca 220px, créditos
  pointsize 22 — mesmo tamanho visual do Marsh/Pup.

* Fri Jun 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.7-1
- Substitui a abordagem de extensão de fotos (que gerava borda artificial
  visível) por um recorte 4:3 nativo das imagens originais de alta resolução
  (Wikimedia Commons, 3:2, 4000–5565px de altura). As 6 fotos são recortadas
  centradas para 4:3, escaladas para 1920×1440 e têm logo+créditos inseridos
  no canto inferior direito. Remove a seção §6 do %build (não há mais
  extensão por espelho/blur); fotos já chegam como PNGs 1920×1440 na source.

* Fri Jun 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.6-1
- Corrige créditos CC BY-SA cortados e texto invertido abaixo da logo (BUG-27):
  a extensão 3:2 (1.0.5) cortava ~64px de cada lateral em telas 4:3, ocultando
  os créditos no canto esquerdo. O espelho invertia a zona do logo CapivaraOS
  (~y=990-1075), gerando texto de cabeça para baixo. Nova abordagem: 4:3
  (1920×1440), espelho nos 180px do topo (join perfeito) e fill suave amostrado
  de y≈900 no rodapé (acima da zona do logo), sem texto invertido nem borrão
  visível.

* Fri Jun 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.5-1
- Substitui extensão por blur (1.0.4) por espelho de reflexão: os primeiros e
  últimos 100px de cada foto são invertidos (-flip) e usados como extensão. O
  join é matematicamente perfeito (mesma linha da foto na costura), sem borrão
  visível no seletor de fundos ou na área de trabalho.
- Altera proporção alvo de 4:3 (1920×1440) para 3:2 (1920×1280), correspondendo
  à resolução exata do VM de testes (1024×682). Em monitores 16:9, o zoom recorta
  apenas os 100px espelhados de cada extremidade, preservando o conteúdo original.

* Fri Jun 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.4-1
- Corrige fotos com barras pretas em cima e embaixo (regressão do 1.0.3): a
  abordagem 'scaled' escondia os créditos mas criava barras visíveis. Nova
  solução: estende cada foto 16:9 (1920x1080) para 4:3 (1920x1440) adicionando
  180px de borda borrada no topo e rodapé. Com 'zoom' em telas 4:3 (VMs), encaixa
  perfeitamente sem barras; em 16:9, o zoom recorta apenas a zona borrada das
  extremidades, mantendo o conteúdo original (e créditos CC BY-SA) visível.
- Reverte picture-options de foto de 'scaled' de volta para 'zoom' (agora seguro
  com as fotos estendidas para 4:3).

* Fri Jun 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.3-1
- Dobra o tamanho da logo no painel "Sistema" (Sobre): substitui fedora_logo_med.png
  com imagem 192x192 (preenchimento total do AdwClamp) em vez de 279x80, fazendo
  a logo aparecer 2.4x maior verticalmente no painel.
- Corrige créditos das fotos de capivara cortados pelo modo zoom: fotos 1920x1080
  (16:9) em telas 4:3 sofriam crop de ~170px nas laterais, ocultando os créditos
  CC BY-SA no canto inferior esquerdo. Muda picture-options de zoom para scaled
  nos wallpapers de foto; wallpapers artísticos (sem créditos) continuam em zoom.
- Muda o wallpaper padrão para capivaraos-desktop.png (arte digital, sem créditos
  de terceiros) para melhor experiência visual em modo zoom no desktop padrão.

* Fri Jun 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.2-1
- Corrige logo no painel "Sistema" (Sobre) do gnome-control-center: o Fedora
  44 patcha o gnome-control-center para carregar o logo a partir de caminhos
  FIXOS no codigo (cc-info-entry.c) --  fedora_logo_med.png e
  fedora_whitelogo_med.png (279x80 px) -- ignorando o campo LOGO= do
  os-release. Sobrescrevemos esses arquivos com a logo CapivaraOS, com
  %transfiletriggerin para sobreviver a updates futuros do fedora-logos.
- Define PRETTY_NAME="CapivaraOS Snout 1.0.2" (versao completa no os-release).

* Thu Jun 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.1-1
- Corrige o dialogo "Habilitar repositorios de programas de terceiros?" do
  GNOME Software reaparecendo indefinidamente na sessao live: tanto
  "Ignorar" quanto "Habilitar" disparam uma acao privilegiada via polkit
  que exige autenticacao de admin, e o liveuser nao tem senha para
  autenticar -- a decisao nunca era gravada. Pre-gravamos o estado em
  /var/lib/fedora-third-party/state como "nao", coerente com a postura
  do CapivaraOS de nao habilitar repositorios de terceiros por padrao.

* Thu Jun 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-2
- Corrige logo do Fedora na tela de boas-vindas (gnome-initial-setup) e no
  painel "Sobre" do GNOME Settings: essas telas usam uma tabela fixa, no
  codigo, de nomes de icone por distro reconhecida (fedora-logo-icon,
  ubuntu-logo-icon, opensuse-logo-icon), nao o LOGO= do os-release.
  Sobrescrevemos o conteudo de fedora-logo-icon com a logo do CapivaraOS
  (com file trigger para sobreviver a updates futuros do fedora-logos)
- Define accent-color=green (verde, cor da marca) como padrao via dconf
- Adiciona tamanho de icone 36x36 (usado pelo fedora-logo-icon)

* Thu Jun 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.0.0-1
- Versao inicial do CapivaraOS Snout (Fedora 44, GNOME)
