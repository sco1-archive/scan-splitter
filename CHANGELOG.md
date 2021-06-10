# Changelog
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (`<major>`.`<minor>`.`<patch>`)

## [v1.1.0]
### Added
* Add the `scansplitter aggregate` data aggregation pipeline to aggregate a directory of anthro measurements into a single CSV.

### Changed
* Consolidated scan files are now split into CSVs rather than preserving the formatting of the source file.
* Headers are now written into the measurements & landmarks CSVs when split out of the consolidated scan file.

## [v1.0.0]
Initial release
