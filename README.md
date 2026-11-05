# CapivaraOS Snout — Fedora 44 (GNOME)

Variante do CapivaraOS construída sobre o ambiente **GNOME** oficial do
Fedora (Workstation), usando as mesmas ferramentas das demais spins do
projeto: `kickstart` + `livemedia-creator` (lorax) para a imagem, e
**Anaconda** como instalador.

Espelha o conjunto de pacotes da spin Marsh (KDE, `../capivaraos-marsh-fedora/`)
— ver `PACKAGES.md` — mas usa a identidade visual **padrão do GNOME**, sem
dock/layout customizado estilo macOS (diferente da Marsh — decisão
explícita para o Snout).

> **Nota sobre o kickstart `upstream/`**: diferente das spins Marsh (KDE) e
> Pup (Xfce), os arquivos `kickstart/upstream/fedora-live-gnome-base.ks` e
> `fedora-gnome-common.ks` **não são cópias literais** do
> `spin-kickstarts` oficial do Fedora — as fontes (pagure.io e
> forge.fedoraproject.org) estão atrás de proteção anti-bot (Anubis,
> desafio JavaScript) que bloqueou o acesso automatizado durante a criação
> deste projeto. Em compensação, o grupo de pacotes usado
> (`@^workstation-product-environment`) foi conferido diretamente no
> comps.xml real do Fedora 44 na máquina de build (não é um palpite) — é
> literalmente o environment-group usado pela ISO oficial do Fedora
> Workstation. Ver comentários nesses arquivos para detalhes.

## Estrutura do projeto

```
capivaraos-snout-fedora/
├── PACKAGES.md                  # Mapeamento de pacotes (espelha a spin Marsh)
├── README.md                    # Este arquivo
├── branding/                    # Assets de identidade visual (fonte para o RPM)
│   ├── backgrounds/               # Wallpapers da marca 2.x (os mesmos do Marsh 2.0)
│   └── icons/                     # Logos do CapivaraOS
├── kickstart/
│   ├── capivaraos-snout.ks        # Kickstart principal (ponto de entrada)
│   ├── capivaraos-post-branding.ks   # %post: idioma/atalho de instalação
│   └── upstream/                  # Kickstarts base do GNOME Live
│       ├── fedora-repo.ks
│       ├── fedora-live-base.ks
│       ├── fedora-gnome-common.ks
│       └── fedora-live-gnome-base.ks
└── rpm/
    ├── capivaraos-branding.spec   # Pacote RPM com toda a identidade visual
    └── build-rpm.sh                # Script auxiliar para gerar o RPM
```

## Visão geral da identidade visual

Todo o branding estático (wallpapers, ícones "Sobre", tema de boot Plymouth,
fundo da tela de login GDM via dconf, `/etc/os-release`, `/etc/issue`,
avatar padrão) é empacotado num único RPM, **`capivaraos-branding`**, que
substitui o `fedora-release-workstation` padrão do Fedora (ver
`rpm/capivaraos-branding.spec`).

Diferente da spin Marsh, o Snout **não** aplica nenhum tema de terceiros
nem customiza o layout do GNOME Shell — usa o ambiente GNOME padrão do
Fedora Workstation, só com a identidade visual (wallpapers/logo/Plymouth/
GDM) do CapivaraOS.

Ver `PACKAGES.md` para o mapeamento completo de pacotes e as diferenças
deliberadas em relação à spin Marsh.

## Pré-requisitos (máquina de build, Fedora 44 x86_64)

```bash
sudo dnf install -y lorax rpm-build ImageMagick git createrepo_c
```

- `lorax` fornece o `livemedia-creator`.
- `rpm-build` + `ImageMagick` são necessários para gerar o RPM
  `capivaraos-branding` (a spec usa `convert` para gerar os ícones em
  vários tamanhos).
- `git` e `createrepo_c` são usados nos passos abaixo.
- O build precisa de acesso à rede para baixar pacotes do Fedora.
- `livemedia-creator --no-virt` precisa rodar como root (usa
  `dnf --installroot` e monta `/dev`, `/proc` etc. no diretório de instalação).

## Build completo (recomendado)

```bash
./build-all.sh
```

Automatiza os três passos abaixo. A ISO final fica em
`/var/tmp/capivaraos-snout-result/CapivaraOS-Snout-1.1.5-x86_64.iso`.

## Passo 1 — Construir o RPM `capivaraos-branding`

```bash
cd rpm
./build-rpm.sh
```

Isso gera `~/rpmbuild/RPMS/noarch/capivaraos-branding-1.1.5-1.*.noarch.rpm`.

## Passo 2 — Disponibilizar o RPM como repositório local

```bash
mkdir -p /var/tmp/capivaraos-snout-repo
cp ~/rpmbuild/RPMS/noarch/capivaraos-branding-*.rpm /var/tmp/capivaraos-snout-repo/
createrepo_c /var/tmp/capivaraos-snout-repo
```

O kickstart (`kickstart/capivaraos-snout.ks`) já referencia
`file:///var/tmp/capivaraos-snout-repo` — ajuste o caminho se mover o
repositório local.

## Passo 3 — Gerar a ISO com `livemedia-creator`

O anaconda (rodando via `--no-virt`) resolve `%include caminho.ks` em relação
ao seu próprio diretório de trabalho, não ao diretório deste projeto. Por
isso, primeiro "achatamos" o kickstart num único arquivo sem `%include` com
`ks-flatten.py`:

```bash
cd kickstart
python3 ks-flatten.py capivaraos-snout.ks > /var/tmp/capivaraos-snout-flat.ks

sudo livemedia-creator --ks=/var/tmp/capivaraos-snout-flat.ks \
    --no-virt --resultdir=/var/tmp/capivaraos-snout-result \
    --project="CapivaraOS Snout" --make-iso --iso-only \
    --iso-name=CapivaraOS-Snout-1.1.5-x86_64.iso \
    --volid="CapivaraOS Snout 1.1.5" --variant="CapivaraOS Snout" \
    --releasever=44
```

A ISO final fica em
`/var/tmp/capivaraos-snout-result/CapivaraOS-Snout-1.1.5-x86_64.iso`.

Logs úteis em caso de problema:
- `/var/tmp/capivaraos-snout-result/*.log` (logs do `livemedia-creator`/lorax)

## Testando a ISO

```bash
qemu-system-x86_64 -m 4096 -enable-kvm \
    -cdrom /var/tmp/capivaraos-snout-result/CapivaraOS-Snout-1.1.5-x86_64.iso
```

## Limitações conhecidas

- **RPM Fusion não está habilitado** (mesma postura conservadora das demais
  spins): o VLC incluso roda com suporte de codecs reduzido.
- **Kickstart `upstream/` reconstruído, não vendorizado**: ver nota no topo
  deste README — ajustes podem ser necessários após o primeiro build real,
  caso algo do GNOME SIG oficial não tenha sido coberto pela reconstrução.

## Comunidade

- Encontrou um bug ou tem uma sugestão? Abra uma [issue](../../issues/new/choose).
- Dúvidas gerais ou ideias em aberto? Use as [Discussions](../../discussions).
- Vulnerabilidade de segurança? Veja [`SECURITY.md`](SECURITY.md) — não abra issue pública.
- Quer contribuir com código? Veja [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.md) do CapivaraOS.
- Licenciado sob [GPLv3](LICENSE).
