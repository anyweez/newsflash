package shared

/**
 * MongoDB representation, which is read and then parsed into a CountryTagger for
 * runtime performance reasons.
 */
type CountryTagData struct {
    CountryName     string
    CountryCode     string
    FreebaseMid     string
    LeaderName      string
    Terms           []string
}