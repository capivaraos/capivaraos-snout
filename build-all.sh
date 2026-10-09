#!/bin/bash
# Build completo do CapivaraOS Snout (Fedora 45 GNOME): instala
# dependências, gera o RPM capivaraos-branding, monta um repositório local
# com ele e constrói a ISO live com livemedia-creator.
#
# Requer privilégios de root (dnf install + livemedia-creator --no-virt) e
# acesso à rede (pacotes do Fedora). Recomenda-se rodar num terminal
# interativo (a senha do sudo será solicitada e o build pode levar bastante
# tempo).
#
# Uso:
#   ./build-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR=/var/tmp/capivaraos-snout-repo
RESULT_DIR=/var/tmp/capivaraos-snout-result
ISO_NAME=CapivaraOS-Snout-2.0.0-alpha11-x86_64.iso

echo "==> 1/4: Instalando dependências (lorax, rpm-build, ImageMagick, git, createrepo_c)..."
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c

echo "==> 2/4: Construindo RPMs (capivaraos-branding + capivara-central)..."
"$SCRIPT_DIR/rpm/build-rpm.sh"
"$SCRIPT_DIR/apps/capivara-central/rpm/build-rpm.sh"

echo "==> 3/4: Criando repositório local em ${REPO_DIR}..."
# BUG CORRIGIDO (build anterior): ~/rpmbuild/RPMS/noarch/ acumula RPMs
# "capivaraos-branding" de TODAS as spins buildadas na mesma máquina (Marsh,
# Pup, Snout). Um filtro por versão sozinho não basta -- num build real,
# Pup e Snout compartilhavam a mesma Version (1.0.0) e o dnf instalou
# silenciosamente o RPM do Pup no lugar do Snout (Release mais alto
# "ganhava"), causando wallpapers/seletor de fundo errados e
# Requires=lightdm-gtk incompatível.
# Agora resolvemos a NEVRA EXATA deste spec (Version E Release) via
# "rpmspec -q", garantindo que copiamos só o RPM desta spin, independente
# do que mais estiver no diretório compartilhado.
sudo rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
# Resolve a NEVRA EXATA de cada spec (Version E Release) e copia só o RPM desta
# spin — independente do que mais esteja no ~/rpmbuild/RPMS compartilhado.
for SPEC in "$SCRIPT_DIR/rpm/capivaraos-branding.spec" \
            "$SCRIPT_DIR/apps/capivara-central/rpm/capivara-central.spec"; do
    NEVRA=$(rpmspec -q --qf '%{name}-%{version}-%{release}.%{arch}\n' "$SPEC" | head -1)
    RPM_FILE="$HOME/rpmbuild/RPMS/noarch/${NEVRA}.rpm"
    [ -f "$RPM_FILE" ] || { echo "ERRO: RPM esperado não encontrado: ${RPM_FILE}" >&2; exit 1; }
    cp -v "$RPM_FILE" "$REPO_DIR/"
done
# ── COS Config Center (app de configuração do sistema) ──────────────────────
# Não é buildado aqui: vem JÁ ASSINADO do nosso repositório, o mesmo pacote
# que o usuário recebe por update. Baixamos a versão mais nova do canal e
# conferimos a assinatura com a chave pública do projeto (num rpmdb isolado)
# antes de pôr no repo local — a confiança vem da assinatura, não do host.
# Canal: "testing" até o pacote ser promovido; depois COS_CONFIG_CHANNEL=stable.
COS_CONFIG_CHANNEL="${COS_CONFIG_CHANNEL:-testing}"
COS_CONFIG_URL="https://repo.capivaraos.org/snout/f45/x86_64/${COS_CONFIG_CHANNEL}/"
echo "  baixando cos-config de ${COS_CONFIG_URL}"
_CC=$(mktemp -d)
cat > "$_CC/cos-config.repo" <<EOF
[cos-config-src]
name=cos-config-src
baseurl=${COS_CONFIG_URL}
enabled=1
gpgcheck=0
EOF
dnf -q -y --setopt=reposdir="$_CC" --setopt=cachedir="$_CC/cache" \
    --disablerepo='*' --enablerepo=cos-config-src --releasever=45 \
    download --destdir="$_CC/out" cos-config
COS_CONFIG_RPM=$(find "$_CC/out" -name 'cos-config-*.noarch.rpm' | sort -V | tail -1)
[ -n "$COS_CONFIG_RPM" ] || { echo "ERRO: não consegui baixar o cos-config de ${COS_CONFIG_URL}" >&2; exit 1; }
rpm --dbpath "$_CC/db" --import "$SCRIPT_DIR/keys/RPM-GPG-KEY-capivaraos"
rpm --dbpath "$_CC/db" -K "$COS_CONFIG_RPM" | grep -q 'digests signatures OK$' \
    || { echo "ERRO: assinatura inválida em $(basename "$COS_CONFIG_RPM"); não entra na ISO." >&2; exit 1; }
rm -f "$REPO_DIR"/cos-config-*.rpm
cp -v "$COS_CONFIG_RPM" "$REPO_DIR/"
rm -rf "$_CC"
createrepo_c "$REPO_DIR"

echo "==> 4/4: Gerando ISO com livemedia-creator (pode levar bastante tempo)..."
sudo rm -rf "$RESULT_DIR"

# O anaconda (rodando via --no-virt/unshare) resolve "%include caminho.ks"
# em relação ao seu próprio cwd, que não é o diretório deste projeto — por
# isso "achatamos" o kickstart num único arquivo sem %include antes de
# chamar o livemedia-creator. Ver kickstart/ks-flatten.py.
FLAT_KS=/var/tmp/capivaraos-snout-flat.ks
sudo rm -f "$FLAT_KS"
( cd "$SCRIPT_DIR/kickstart" && python3 ks-flatten.py capivaraos-snout.ks > "$FLAT_KS" )

LIVEMEDIA_LOG="$SCRIPT_DIR/livemedia.log"

sudo livemedia-creator --ks="$FLAT_KS" \
    --no-virt --resultdir="$RESULT_DIR" \
    --logfile="$LIVEMEDIA_LOG" \
    --project="CapivaraOS Snout" --make-iso --iso-only \
    --iso-name="$ISO_NAME" \
    --volid="CapivaraOS Snout 2.0.0 alpha11" --variant="CapivaraOS Snout" \
    --releasever=45

# ── Título do menu de boot da mídia live (grub) ─────────────────────────────
# O lorax gera "CapivaraOS Snout 45" (@PRODUCT@ + @VERSION@=releasever). Queremos
# que o título ACOMPANHE a versão do CapivaraOS + Fedora: "CapivaraOS Snout 2 45"
# (2 = série do CapivaraOS, 45 = Fedora base). Derivamos dinamicamente do ISO_NAME
# (série do CapivaraOS) e do releasever (Fedora), então ao subir qualquer um o
# título acompanha sozinho. Edita os dois grub.cfg (BIOS /boot/grub2, UEFI
# /EFI/BOOT) na ISO com xorriso e reimplanta o checksum (implantisomd5) -- senão
# "Test this media" falha. Só cosmético (menu do pendrive live); passo NÃO-fatal.
ISO_PATH="${RESULT_DIR}/${ISO_NAME}"
FVER=45
COS_MAJOR=$(echo "$ISO_NAME" | sed -E 's/^CapivaraOS-Snout-([0-9]+)\..*/\1/')
MENU_TITLE="CapivaraOS Snout ${COS_MAJOR} ${FVER}"
echo
echo "==> Ajustando o título do menu de boot da mídia para: ${MENU_TITLE}"
if command -v xorriso >/dev/null 2>&1; then
    _GW=$(mktemp -d)
    for GCFG in /EFI/BOOT/grub.cfg /boot/grub2/grub.cfg; do
        _b="${_GW}/$(echo "$GCFG" | tr '/' '_')"
        xorriso -osirrox on -indev "$ISO_PATH" -extract "$GCFG" "$_b" 2>/dev/null || continue
        sed -i "s|CapivaraOS Snout ${FVER}|${MENU_TITLE}|g" "$_b"
    done
    if xorriso -indev "$ISO_PATH" -outdev "${ISO_PATH}.new" -boot_image any replay \
            -update "${_GW}/_EFI_BOOT_grub.cfg"   /EFI/BOOT/grub.cfg \
            -update "${_GW}/_boot_grub2_grub.cfg" /boot/grub2/grub.cfg \
            -commit >/dev/null 2>&1 && [ -s "${ISO_PATH}.new" ]; then
        mv "${ISO_PATH}.new" "$ISO_PATH"
        command -v implantisomd5 >/dev/null 2>&1 && implantisomd5 --force "$ISO_PATH" >/dev/null 2>&1
        echo "==> Título do menu de boot ajustado."
    else
        rm -f "${ISO_PATH}.new"
        echo "AVISO: não consegui reescrever o grub.cfg da ISO; o menu fica 'Snout ${FVER}' (só cosmético)." >&2
    fi
    rm -rf "$_GW"
fi

# ── Trava contra ISO sem os updates do Fedora (BUG-29) ─────────────────────
# As ISOs 1.1.2/1.1.3 da spin Marsh saíram só com o Fedora 44 GA porque o repo
# de updates não foi aplicado na composição — o nome "updates" é reservado
# pelo Anaconda e o repo era ignorado em silêncio (ver
# kickstart/upstream/fedora-repo.ks). Sem esta trava, uma ISO desatualizada
# passa batido até o usuário ver ~1000 pacotes de update no primeiro boot.
# Comparamos o kernel que entrou na ISO com o mais novo do repo de updates.
echo
echo "==> Verificando se a ISO recebeu os updates do Fedora..."
ISO_KERNEL=$(grep -o "vmlinuz-[0-9][^ ']*" "$LIVEMEDIA_LOG" 2>/dev/null \
    | sed 's/vmlinuz-//; s/\.x86_64$//' | sort -V | tail -1)
_TMPREPO=$(mktemp -d)
cat > "$_TMPREPO/ucheck.repo" <<EOF
[ucheck]
name=ucheck
mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f45&arch=x86_64
enabled=1
EOF
LATEST_KERNEL=$(dnf -q --setopt=reposdir="$_TMPREPO" --disablerepo='*' --enablerepo=ucheck \
    --releasever=45 repoquery --qf '%{version}-%{release}\n' kernel-core 2>/dev/null \
    | sort -V | tail -1)
rm -rf "$_TMPREPO"

if [ -z "$ISO_KERNEL" ]; then
    echo "AVISO: não consegui extrair o kernel da ISO de ${LIVEMEDIA_LOG}; trava pulada." >&2
elif [ -z "$LATEST_KERNEL" ]; then
    echo "AVISO: não consegui consultar o repo updates (rede?); trava pulada." >&2
elif [ "$ISO_KERNEL" != "$LATEST_KERNEL" ]; then
    echo "ERRO: a ISO saiu com kernel ${ISO_KERNEL}, mas o repo updates tem ${LATEST_KERNEL}." >&2
    echo "      O repo de updates NÃO foi aplicado — a ISO está DESATUALIZADA (BUG-29)." >&2
    exit 1
else
    echo "==> OK: ISO com kernel ${ISO_KERNEL} (bate com o repo updates)."
fi

echo
echo "==> Concluído! ISO em: ${RESULT_DIR}/${ISO_NAME}"
