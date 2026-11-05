# =============================================================================
# CapivaraOS Snout — pós-instalação: ajustes finos de branding
# =============================================================================
#
# A maior parte do branding (wallpapers, ícones "Sobre o Sistema", tema
# Plymouth, fundo do GDM via dconf, /etc/os-release, /etc/issue, avatar
# padrão) já é instalada pelo pacote `capivaraos-branding` (ver
# ../rpm/capivaraos-branding.spec). Este post-script cobre apenas o que não
# cabe num pacote RPM: regeneração da initramfs com o tema Plymouth, idioma
# de fallback e o ícone "Instalar CapivaraOS" na sessão live.

%post
# ── Regera a initramfs com o tema Plymouth do CapivaraOS ────────────────────
# Ver justificativa detalhada na spin Marsh/Pup (idêntica aqui): o
# kernel-core gera a initramfs ANTES do %posttrans do capivaraos-branding,
# então regeneramos aqui, depois de toda a transação de pacotes.
#
# --no-hostonly (e --no-hostonly-cmdline) e OBRIGATORIO (BUG-40, comprovado
# 2026-08-17 no Pup). Este %post roda no BUILD; sem os flags o initramfs sai so
# com os drivers de storage da MAQUINA DE BUILD. O live nao sofre (drivers
# genericos do USB), mas o SISTEMA INSTALADO herda esse initramfs e, num
# hardware com storage diferente do build, NAO acha o disco raiz -> "Not all
# disks have been found" -> emergency mode. Generico inclui todos os drivers.
# Depois de instalado, updates de kernel regeneram hostonly no alvo (correto).
for kver in $(ls /lib/modules); do
    dracut -f --no-hostonly --no-hostonly-cmdline "/boot/initramfs-${kver}.img" "${kver}"
done

# ── BLOCKER de boot (PROD-133): remove o /etc/kernel/cmdline "fantasma" ──────
# Este %post roda no BUILD da live. O arquivo /etc/kernel/cmdline nasce aqui com
# o UUID de raiz do AMBIENTE DE BUILD e SEM rootflags=subvol=root (btrfs). O
# instalador live (liveimg) COPIA o rootfs pro alvo, arrastando esse arquivo; o
# Anaconda escreve as entradas BLS do install corretas mas NAO corrige este
# arquivo. Como o kernel-install compoe a linha options= de TODO kernel novo a
# partir dele, o 1o update de kernel gera uma BLS com root inexistente/sem subvol
# -> dracut emergency mode. Removendo (como faz o live padrao do Fedora), o
# kernel-install passa a derivar do /proc/cmdline REAL do sistema instalado
# (root=UUID correto + rootflags=subvol=root), valido p/ qualquer layout. Como o
# %post roda no build, nao da p/ escrever o valor certo aqui -> remover e o certo.
# Espelhado do Marsh (commit 0bbc113). Ver reference_etc_kernel_cmdline_ghost.
rm -f /etc/kernel/cmdline /usr/lib/kernel/cmdline

# ── Idioma: pt_BR com fallback para en_US ───────────────────────────────────
if [ -f /etc/locale.conf ]; then
    sed -i '/^LANGUAGE=/d' /etc/locale.conf
fi
echo 'LANGUAGE=pt_BR:en_US' >> /etc/locale.conf

# ── Ícone "Instalar CapivaraOS" — APENAS na sessão live ─────────────────────
# O instalador é fornecido pelo Anaconda live via
# /usr/share/applications/liveinst.desktop (NoDisplay=true). Em sessões
# GNOME, o script livesys-gnome (pacote livesys-scripts,
# /usr/libexec/livesys/sessions.d/livesys-gnome) faz NoDisplay=false e
# RENOMEIA o arquivo para anaconda.desktop (para aparecer no GNOME Shell
# Activities), além de adicioná-lo aos favoritos da dash — e só faz isso na
# sessão live (liveuser), nunca no sistema já instalado. Aqui apenas
# renomeamos/reidentificamos o liveinst.desktop com o nome e o ícone do
# CapivaraOS ANTES disso acontecer; a renomeação/mv do livesys-gnome
# preserva nosso Name=/Icon= (só altera NoDisplay e o caminho do arquivo).
if [ -f /usr/share/applications/liveinst.desktop ]; then
    sed -i \
        -e '/^Name\[/d' \
        -e '/^GenericName\[/d' \
        -e '/^Comment\[/d' \
        -e 's/^Name=.*/Name=Instalar CapivaraOS/' \
        -e 's/^GenericName=.*/GenericName=Instalar CapivaraOS/' \
        -e 's/^Comment=.*/Comment=Instala o CapivaraOS permanentemente no computador/' \
        -e 's#^Icon=.*#Icon=/usr/share/pixmaps/capivaraos-white.png#' \
        /usr/share/applications/liveinst.desktop
    grep -q '^Name=Instalar CapivaraOS' /usr/share/applications/liveinst.desktop || \
        echo 'Name=Instalar CapivaraOS' >> /usr/share/applications/liveinst.desktop
    grep -q '^Icon=/usr/share/pixmaps/capivaraos-white.png' /usr/share/applications/liveinst.desktop || \
        echo 'Icon=/usr/share/pixmaps/capivaraos-white.png' >> /usr/share/applications/liveinst.desktop
fi

%end
