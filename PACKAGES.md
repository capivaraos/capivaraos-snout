# Mapeamento de pacotes: CapivaraOS Snout (Fedora 44, GNOME)

Espelha o conjunto de pacotes da spin Marsh (KDE) — ver
`../capivaraos-marsh-fedora/PACKAGES.md` — trocando o ambiente de desktop e
removendo a seção exclusiva do tema macOS/WhiteSur (o Snout usa o GNOME
padrão, sem dock/layout customizado).

Convenções do kickstart Fedora:
- `@nome` = grupo comps
- `@^nome` = grupo "environment" (define o ambiente todo)
- `-pacote` = remove um pacote que viria por dependência/grupo

## ===== SISTEMA BASE =====

| Pacote | Observações |
|---|---|
| `langpacks-pt_BR`, `glibc-langpack-pt` | Pacotes de idioma pt-BR |
| `glibc-all-langpacks` | Já incluso na base live (fedora-live-base) |
| `linux-firmware` | Já vem por padrão com o kernel no Fedora |

## ===== DESKTOP GNOME =====

| Pacote | Observações |
|---|---|
| `@^workstation-product-environment` | Environment group oficial do Fedora Workstation (GNOME) — conferido no comps.xml real desta máquina de build (ver nota em kickstart/upstream/fedora-gnome-common.ks). Já inclui Firefox, LibreOffice, multimídia, impressão e o GNOME completo. |
| `gdm` | Tela de login (incluso no environment group, listado por clareza no spec do branding) |
| `-fedora-release-workstation` | Removido: branding padrão do Fedora Workstation, substituído por `capivaraos-branding` |
| `-desktop-backgrounds-gnome`, `-gnome-shell-extension-background-logo` | Removidos: wallpapers/logo padrão do Fedora, sem dependência reversa de nada do nosso conjunto (conferido via `dnf repoquery --whatrequires`) |

## ===== AUDIO =====

| Pacote |
|---|
| `pipewire`, `pipewire-pulseaudio`, `wireplumber` (inclusos via `@^workstation-product-environment`) |

## ===== INTERNET =====

| Pacote | Observações |
|---|---|
| `firefox` | Incluso via `@^workstation-product-environment` -> grupo `firefox` |
| `thunderbird` | Adicionado explicitamente (não incluso por padrão no Workstation) |
| `NetworkManager` | Já vem na imagem live base |

## ===== OFFICE =====

| Pacote | Observações |
|---|---|
| `@^workstation-product-environment` -> grupo `libreoffice` | LibreOffice base já incluso |
| `libreoffice-langpack-pt-BR` | |
| `libreoffice-help-pt-BR` | |

## ===== MIDIA =====

| Pacote | Observações |
|---|---|
| `vlc` | Disponível nos repos oficiais do Fedora 44. Sem RPM Fusion, codecs proprietários ficam limitados — ver nota em ../capivaraos-marsh-fedora/PACKAGES.md (mesma postura conservadora adotada aqui). |
| `gimp` | |

## ===== INSTALADOR =====

| Pacote | Observações |
|---|---|
| Anaconda nativo (`anaconda-live`, `@anaconda-tools`) | Mesma decisão da spin Marsh: não usamos Calamares |

## ===== UTILITARIOS =====

| Pacote |
|---|
| `gparted` |
| `htop` |
| `fastfetch` |
| `curl` |
| `wget` |
| `zip` |
| `unzip` |
| `rsync` |

## ===== DESENVOLVIMENTO =====

| Pacote | Observações |
|---|---|
| `git` | |
| `nano` | |
| `vim-enhanced` | |
| `@development-tools` | Grupo com gcc, make, etc. |

## ===== APPS PRÓPRIOS DO CAPIVARAOS (série 2.x) =====

| Pacote | Observações |
|---|---|
| `capivaraos-branding` | Identidade visual (wallpapers, logo, Plymouth, greeter GDM, os-release). Buildado neste repo (`rpm/capivaraos-branding.spec`). |
| `capivara-central` | COS Dev Center — app de onboarding de 1º boot (GTK4/libadwaita) que liga os extras opcionais da estação de dev (IA local, trilhas, GPU, ferramentas, gh). Buildado neste repo (`apps/capivara-central/`). |
| `cos-config` | COS Config Center — central de configuração do sistema (0.11.1). **NÃO é buildado aqui**: vem já ASSINADO do repositório (`repo.capivaraos.org/snout/f45/x86_64/<canal>`, canal via `COS_CONFIG_CHANNEL`, padrão `testing`), baixado e verificado por assinatura (gpgcheck + chave do projeto) no passo 3 do `build-all.sh` antes de entrar na ISO. Mesmo pacote que o usuário recebe por update. Épico PROD-5 / integração PROD-141. |

## ===== FONTES =====

| Pacote |
|---|
| `liberation-fonts` |
| `dejavu-fonts-all` |
| `google-noto-sans-fonts`, `google-noto-serif-fonts`, `google-noto-emoji-fonts` |

## ===== IMPRESSAO =====

| Pacote | Observações |
|---|---|
| `cups` | Já incluso via `@^workstation-product-environment` -> grupo `printing`; listado por clareza |
| `system-config-printer` | Adicionado explicitamente, por paridade com as demais spins |

## ===== DIFERENÇAS DELIBERADAS EM RELAÇÃO À SPIN MARSH (KDE) =====

- **Sem tema macOS/WhiteSur**: o Snout usa o GNOME Shell padrão, sem
  dock/painel customizado. Decisão explícita (ver discussão de criação do
  projeto) — diferente da Marsh, que replica o layout do CapivaraOS
  original (Debian).
- **Wallpaper/login**: em vez de scripts de runtime (capivaraos-set-wallpaper
  da Marsh/Pup), o Snout usa o mecanismo padrão do GNOME: dconf system-wide
  (`/etc/dconf/db/local.d/` para o usuário, `/etc/dconf/db/gdm.d/` para o
  GDM) — ver rpm/capivaraos-branding.spec.
- **Seletor de wallpaper**: em vez de pacotes de wallpaper estilo Plasma
  (metadata.json por imagem), um único XML em
  `/usr/share/gnome-background-properties/` registra todos os wallpapers no
  painel "Fundo" do GNOME Settings.

## ===== live.list.chroot (equivalente) =====

| Pacote |
|---|
| `livesys-scripts` (usa o script `livesys-gnome` para a sessão live), `anaconda-live`, `@anaconda-tools`, `dracut-live` (parte do `fedora-live-base`) |
