#version=DEVEL
# =============================================================================
# CapivaraOS Snout - Fedora 45 (GNOME) - kickstart principal
# =============================================================================
#
# Spin "completa" do CapivaraOS sobre o ambiente GNOME oficial do Fedora
# (Workstation), espelhando o conjunto de pacotes da spin Marsh (KDE) — ver
# PACKAGES.md. Identidade visual padrão do GNOME (sem dock/layout estilo
# macOS, diferente da Marsh — decisão explícita para o Snout).
#
# NOTA CapivaraOS: kickstart/upstream/fedora-live-gnome-base.ks e
# fedora-gnome-common.ks NÃO são cópias literais do spin-kickstarts oficial
# (pagure.io/forge.fedoraproject.org bloqueiam acesso automatizado via
# Anubis) — foram reconstruídos com base no environment-group real
# "workstation-product-environment", conferido no comps.xml desta máquina
# de build. Ver comentários nesses arquivos para detalhes.
#
# Uso (ver README.md para detalhes; ./build-all.sh automatiza tudo isto):
#   cd kickstart && python3 ks-flatten.py capivaraos-snout.ks > /var/tmp/capivaraos-snout-flat.ks
#   livemedia-creator --ks=/var/tmp/capivaraos-snout-flat.ks \
#       --no-virt --resultdir=/var/tmp/capivaraos-snout-result \
#       --project="CapivaraOS Snout" --make-iso --iso-only \
#       --iso-name=CapivaraOS-Snout-1.0.1-x86_64.iso \
#       --volid="CapivaraOS Snout 1.0.1" --variant="CapivaraOS Snout" \
#       --releasever=45
#
# NOTA: o anaconda resolve "%include caminho.ks" em relação ao seu próprio
# cwd (não ao diretório deste arquivo), por isso o ks-flatten.py acima é
# necessário — ver kickstart/ks-flatten.py.

%include upstream/fedora-live-gnome-base.ks

# ── Repositório local com o RPM capivaraos-branding ─────────────────────────
# Gerado por ../build-all.sh (rpm/build-rpm.sh + createrepo_c) em
# /var/tmp/capivaraos-snout-repo. Nome de diretório distinto do usado pelas
# outras spins para permitir buildar todas na mesma máquina sem um repo
# local sobrescrever o outro.
repo --name=capivaraos-local --baseurl=file:///var/tmp/capivaraos-snout-repo

# ── IDIOMA / TECLADO / FUSO (mesma convenção das demais spins) ─────────────
lang pt_BR.UTF-8
keyboard --xlayouts='br-abnt2' --vckeymap=br-abnt2
timezone America/Sao_Paulo --utc
network --hostname=capivaraos

# =============================================================================
# PACOTES — ver PACKAGES.md
# =============================================================================
%packages

# ── Identidade visual: usamos nosso próprio pacote de branding em vez do
# branding padrão do Fedora Workstation (wallpapers, plymouth, GDM,
# os-release). Ver rpm/capivaraos-branding.spec.
-fedora-release-workstation
# Pacotes de wallpaper/extensão "Fedora" que viriam por padrão no
# Workstation: removidos para não competir com o branding do CapivaraOS
# (ver "dnf repoquery --whatrequires" conferido no ambiente de build —
# nenhum pacote do nosso conjunto depende deles, seguro excluir).
-desktop-backgrounds-gnome
-gnome-shell-extension-background-logo
capivaraos-branding

# Tema Plymouth do CapivaraOS (capivaraos.script) é um tema "script": precisa
# do plugin script.so do plymouth para ser renderizado. Ver justificativa
# detalhada na spin Marsh (mesmo motivo, idêntico aqui).
plymouth-plugin-script

# Fedora Media Writer não é necessário e tem branding/conteúdo padrão do Fedora
-mediawriter

# ===== SISTEMA BASE (idioma) =====
langpacks-pt_BR
glibc-langpack-pt

# ===== OFFICE: tradução pt-BR do LibreOffice =====
# (LibreOffice em si já vem via @^workstation-product-environment -> grupo
# "libreoffice", ver fedora-gnome-common.ks)
libreoffice-langpack-pt-BR
libreoffice-help-pt-BR

# ===== INTERNET =====
# Firefox já vem via @^workstation-product-environment -> grupo "firefox"
thunderbird

# ===== MIDIA =====
vlc
gimp

# ===== UTILITARIOS =====
gparted
htop
fastfetch
curl
wget
zip
unzip
rsync

# ===== DESENVOLVIMENTO =====
git
nano
vim-enhanced
@development-tools
# COS Dev Center: app de onboarding de 1o boot (GTK4/libadwaita) que liga os
# extras opcionais da estacao de dev em um clique (IA local, trilhas, GPU,
# ferramentas, gh) e o "Atualizar o CapivaraOS" (PROD-116/117).
capivara-central
# -- COS Config Center: central de configuracao (codecs, firewall, discos, rede,
# idioma...). Pacote ja assinado, baixado do nosso repositorio pelo build-all.sh
# para o repo local capivaraos-local.
cos-config

# ===== UPDATE IN-PLACE (repo assinado + upgrade de versao) =====
# capivaraos-repos: instala o repositorio de updates assinado (repo.capivaraos.org)
# + a chave GPG do projeto, habilitando o "atualize sem formatar" via dnf/GNOME
# Software. capivaraos-upgrade: ferramenta de upgrade de versao (2.x -> ...) com
# snapshot pre-upgrade. Ambos buildados localmente pelo build-all.sh; o
# capivaraos-upgrade depende de capivaraos-repos. (FEAT-111, PROD-116/117.)
capivaraos-repos
capivaraos-upgrade

# ===== FONTES =====
liberation-fonts
dejavu-fonts-all
google-noto-sans-fonts
google-noto-serif-fonts
google-noto-emoji-fonts

# ===== IMPRESSAO =====
# cups + ferramentas básicas já vêm via @^workstation-product-environment ->
# grupo "printing"; mantemos o system-config-printer explícito por
# paridade com as demais spins (GUI clássica de configuração de impressoras).
system-config-printer

# ===== SNAPSHOTS ("atualize sem medo") =====
# Btrfs é o padrão do instalador; snapper dá os snapshots pré/pós. A config
# "root" do snapper é criada no 1o boot pelo capivaraos-snapper-setup.service
# (do capivaraos-branding) — sem ela o capivaraos-upgrade não tira snapshot
# automático antes do upgrade in-place (PROD-116). btrfs-assistant = GUI.
snapper
btrfs-assistant

%end

# =============================================================================
# Post-scripts específicos do CapivaraOS
# =============================================================================
%include capivaraos-post-branding.ks
