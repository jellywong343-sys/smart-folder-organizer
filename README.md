# Smart Folder Organizer

[绠€浣撲腑鏂嘳(README.zh-CN.md)

Preview, organize, and undo folder cleanup using file categories, extensions, or modification month.

## Highlights

- Preview-only by default; files move only with `--apply`.
- Organize by category, extension, or `YYYY-MM` date.
- Keeps an undo manifest after each applied run.
- Resolves name collisions without overwriting files.
- Python standard library only; Python 3.10+.

## Install

```bash
git clone https://github.com/jellywong343-sys/smart-folder-organizer.git
cd smart-folder-organizer
python -m pip install -e .
```

## Usage

```bash
smart-organize ~/Downloads
smart-organize ~/Downloads --mode extension
smart-organize ~/Downloads --mode date --apply
smart-organize ~/Downloads --undo
```

## Safety

The default command only prints a plan. Back up irreplaceable files before applying bulk changes.

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT



