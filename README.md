# driftwm dotfiles

> Персональная риса для **driftwm** на EndeavourOS. Минимализм, canvas-навигация и кастомные виджеты.

## Концепция

- **driftwm** — Wayland compositor с бесконечным canvas. Окна размещаются на плоскости, камера двигается между ними.
- Рабочий стол разделён на две зоны:
  - **Home** (`mod+a`) — дашборд с виджетами (часы, погода, статистика, календарь)
  - **Рабочая зона** — основные окна (браузер, терминал, мессенджеры, Spotify)

## Структура

```
.
├── config.toml              # Главный конфиг driftwm
├── alacritty/               # Терминал + dark/light цветовые схемы
├── fuzzel/                  # Ланчер приложений
├── scripts/                 # Автоматизация и OSD
│   ├── media-osd.sh         # OSD при смене трека в Spotify
│   ├── volume-osd.sh        # OSD громкости (устарел, сейчас swayosd)
│   ├── theme-toggle.sh      # Переключение light/dark темы
│   ├── theme-apply.sh       # Применение темы к driftwm + waybar
│   ├── wallpaper-cycle.sh   # Смена GLSL-шейдеров фона
│   └── ...
├── wallpapers/              # GLSL-шейдеры (static + animated)
└── widgets/                 # Python-виджеты для Home view
    ├── launch.sh            # Запускалка всех виджетов
    ├── clock_widget.py
    ├── stats_widget.py
    ├── weather_widget.py
    └── ...
```

## Что сделано

### Внешний вид
- **Декорации** — кастомные цвета заголовков, скругление углов, тени
- **Фон** — процедурные GLSL-шейдеры (меняются по хоткею)
- **Прозрачность + blur** — для Alacritty, Telegram, SwayNC

### Управление
- **Хоткеи** на `mod` (Super) для всех действий: окна, навигация, зум, скриншоты, запись экрана
- **Mouse + touchpad** — drag-to-pan, pinch-to-zoom, жесты для resize
- **Snap** — магнитное прилипание окон друг к другу

### OSD (On-Screen Display)
- **Громкость / микрофон / яркость** — через `swayosd` (бар сверху по центру)
- **Смена трека в Spotify** — кастомный скрипт на `playerctl` + `swayosd-client`

### Автозапуск
- `swaync` — центр уведомлений
- `swayosd-server` — сервер OSD
- `waybar` — два инстанса (taskbar слева, tray снизу)
- `swayidle` — затемнение экрана
- `cliphist` — история буфера обмена
- Виджеты дашборда (через Alacritty + Python)

### Темы
- Переключение **light / dark** по `mod+Shift+d`
- Меняются: цвета driftwm, шейдер фона, цвета Alacritty, CSS waybar

## Зависимости

```bash
# Core
sudo pacman -S driftwm alacritty fuzzel waybar swaync swayosd

# Tools
sudo pacman -S playerctl brightnessctl wl-clipboard cliphist grim slurp

# Widgets (Python)
pip install rich  # или через uv/pipx

# Тема курсора и иконок
sudo pacman -S capitaine-cursors papirus-icon-theme
```

## Установка

```bash
# Клонировать в ~/.config/driftwm
git clone git@github.com:siers22/driftwm-dotfiles.git ~/.config/driftwm

# Симлинк для waybar (если нужно)
ln -s ~/.config/driftwm/waybar ~/.config/waybar
```

> **Важно:** `config.toml` ожидает хардкодные пути к `~/.config/driftwm/...`. Если ставишь в другое место — поправь пути.

## Полезные команды

| Действие | Хоткей |
|----------|--------|
| Терминал | `mod+Enter` |
| Ланчер | `mod+d` |
| Home view | `mod+a` |
| Zoom to fit | `mod+w` |
| Fullscreen | `mod+f` |
| Close window | `mod+q` |
| Скриншот области | `mod+Shift+s` |
| Запись экрана | `mod+Shift+r` / `mod+Shift+x` |
| Смена темы | `mod+Shift+d` |
| Смена обоев | `mod+Shift+w` |
| Lock | `mod+l` |

## TODO / Идеи

- [ ] Сохранение / восстановление layout (холста) между сессиями
- [ ] Обложка альбома в музыкальном OSD
- [ ] Больше GLSL-шейдеров на фон

---

*Сделано с болью и удовольствием на EndeavourOS.*
