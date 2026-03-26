# Navidrome Smart Playlists

A collection of 7 smart playlists for [Navidrome](https://www.navidrome.org/), a personal music streaming server.

## Playlists Included

1. **Loved Tracks** - All starred or loved tracks, sorted by date loved or starred
2. **New This Week** - All tracks added in the last 3 days, sorted by album
3. **New This Month** - All tracks added in the last 2 weeks, sorted by album
4. **A Year Ago This Month** - 25 random tracks added approximately 1 year ago
5. **Never Played** - All unplayed tracks, sorted randomly
6. **Most Played** - The 100 most played songs in your library, sorted randomly
7. **Recently Played** - Up to 100 tracks played in the last 30 days, sorted randomly

## Installation

To use these smart playlists in Navidrome:

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/navidrome-smart-playlists.git
   ```

2. Copy the `.nsp` files to your Navidrome playlists directory:
   ```bash
   cp *.nsp /path/to/navidrome/playlists/
   ```
   Or set the `PlaylistsPath` in your Navidrome configuration to point to this repository.

3. Restart Navidrome or trigger a library scan. The playlists will be automatically imported and available in your Navidrome UI.

## Notes

- All playlists are personal and designed for individual use
- Playlist 4 ("A Year Ago This Month") is dynamic and automatically adjusts based on the current month
- Playlists with random sorting will have different track selection each time they're accessed
- Each `.nsp` file contains JSON configuration - ensure valid JSON formatting

## Editing Playlists

To modify these playlists, edit the corresponding `.nsp` file and commit your changes. Navidrome will automatically detect and reimport the playlists on the next library scan.

For more information on creating and managing smart playlists, refer to the [Navidrome Smart Playlists documentation](https://www.navidrome.org/docs/usage/smartplaylists/).
