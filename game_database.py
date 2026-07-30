# -----------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -----------------------------------------------------------------------------
GAME_DATABASE = {
    "Star Fox": {
        "steam_id": 0,
        "metacritic_slug": "nintendo-switch-2/star-fox",
        "opencritic_id": 0,
        "opencritic_slug": "star-fox",
        "backup_peak": 0,
        "release_date": "2026-06-30"
    },
    "Rhythm Heaven Groove": {
        "steam_id": 0,
        "metacritic_slug": "switch/rhythm-heaven-groove",
        "opencritic_id": 20339,
        "opencritic_slug": "rhythm-heaven-groove",
        "backup_peak": 0,
        "release_date": "2026-07-02"
    },
    "Pit Panic": {
        "steam_id": 2491490,
        "metacritic_slug": "pc/pit-panic",
        "opencritic_id": 0,
        "opencritic_slug": "pit-panic",
        "backup_peak": 0
    },
    "Avatar Legends: The Fighting Game": {
        "steam_id": 2424420,
        "metacritic_slug": "pc/avatar-legends-the-fighting-game",
        "opencritic_id": 0,
        "opencritic_slug": "avatar-legends-the-fighting-game",
        "backup_peak": 0,
        "release_date": "2026-07-23"        
    },
    "Esports Manager 2026": {
        "steam_id": 2749950,
        "metacritic_slug": "pc/esports-manager-2026",
        "opencritic_id": 21015,
        "opencritic_slug": "esports-manager-2026",
        "backup_peak": 0
    },
    "Moonlight Peaks": {
        "steam_id": 2209900,
        "metacritic_slug": "pc/moonlight-peaks",
        "opencritic_id": 20950,
        "opencritic_slug": "moonlight-peaks",
        "backup_peak": 0
    },
    "Assassin's Creed Black Flag Resynced": {
        "steam_id": 3751950,
        "metacritic_slug": "pc/assassins-creed-black-flag-resynced",
        "opencritic_id": 0,
        "opencritic_slug": "assassins-creed-black-flag-resynced",
        "backup_peak": 0
    },
    "Echoes of Anicrad": {
        "steam_id": 2244210,
        "metacritic_slug": "pc/echoes-of-aincrad",
        "opencritic_id": 20207,
        "opencritic_slug": "echoes-of-aincrad",
        "backup_peak": 0
    },
    "Ascend to ZERO": {
        "steam_id": 2697940,
        "metacritic_slug": "pc/ascend-to-zero",
        "opencritic_id": 0,
        "opencritic_slug": "ascend-to-zero",
        "backup_peak": 0
    },
    "Denshattack!": {
        "steam_id": 2524850,
        "metacritic_slug": "pc/denshattack",
        "opencritic_id": 20193,
        "opencritic_slug": "denshattack",
        "backup_peak": 0
    },
    "Heave Ho 2": {
        "steam_id": 2802740,
        "metacritic_slug": "pc/heave-ho-2",
        "opencritic_id": 20999,
        "opencritic_slug": "heave-ho-2",
        "backup_peak": 0,
        "release_date": "2026-07-16"
    },
    "Moss: The Forgotten Relic": {
        "steam_id": 3914860,
        "metacritic_slug": "pc/moss-the-forgotten-relic",
        "opencritic_id": 20976,
        "opencritic_slug": "moss-the-forgotten-relic",
        "backup_peak": 0,
        "release_date": "2026-07-16"
    },
    "Fogpiercer": {
        "steam_id": 3219010,
        "metacritic_slug": "pc/fogpiercer",
        "opencritic_id": 0,
        "opencritic_slug": "fogpiercer",
        "backup_peak": 0,
        "release_date": "2026-07-17"
    },
    "Shift at Midnight": {
        "steam_id": 3722330,
        "metacritic_slug": "pc/shift-at-midnight",
        "opencritic_id": 0,
        "opencritic_slug": "shift-at-midnight",
        "backup_peak": 0,
        "release_date": "2026-07-22"  
    },
    "Scarlet Deer Inn": {
        "steam_id": 1553260,
        "metacritic_slug": "pc/scarlet-deer-inn",
        "opencritic_id": 20972,
        "opencritic_slug": "scarlet-deer-inn",
        "backup_peak": 0,
        "release_date": "2026-07-21"
    },
    "Tormentum II": {
        "steam_id": 931060,
        "metacritic_slug": "pc/tormentum-ii",
        "opencritic_id": 0,
        "opencritic_slug": "tormentum-ii",
        "backup_peak": 0,
        "release_date": "2026-07-23"
    },
    "Dinoblade": {
        "steam_id": 3440070,
        "metacritic_slug": "pc/dinoblade",
        "opencritic_id": 0,
        "opencritic_slug": "dinoblade",
        "backup_peak": 0,
        "release_date": "2026-07-23"
    },
    "Splatoon Raiders": {
        "steam_id": 0,  
        "metacritic_slug": "nintendo-switch-2/splatoon-raiders",
        "opencritic_id": 20454,
        "opencritic_slug": "splatoon-raiders",
        "backup_peak": 0,
        "release_date": "2026-07-23"
    },
    "Halo: Campaign Evolved": {
        "steam_id": 2806050,
        "metacritic_slug": "pc/halo-campaign-evolved",
        "opencritic_id": 0,
        "opencritic_slug": "halo-campaign-evolved",
        "backup_peak": 0,
        "release_date": "2026-07-28"
    },
    "Xenoblade Chronicles 2": {
        "steam_id": 0,  
        "metacritic_slug": "nintendo-switch-2/xenoblade-chronicles-2",
        "opencritic_id": 4952,
        "opencritic_slug": "xenoblade-chronicles-2",
        "backup_peak": 0,
        "release_date": "2026-07-30"
    },
    "Mistfall Hunter": {
        "steam_id": 3282300,
        "metacritic_slug": "pc/mistfall-hunter",
        "opencritic_id": 20798,
        "opencritic_slug": "mistfall-hunter",
        "backup_peak": 0,
        "release_date": "2026-07-29"
    },
    "The Relic: First Guardian": {
        "steam_id": 2827820,
        "metacritic_slug": "pc/the-relic-first-guardian",
        "opencritic_id": 0,
        "opencritic_slug": "the-relic-first-guardian",
        "backup_peak": 0,
        "release_date": "2026-07-31"
    },
    "ZeroSpace": {
        "steam_id": 1605850,
        "metacritic_slug": "pc/zerospace",
        "opencritic_id": 0,
        "opencritic_slug": "zerospace",
        "backup_peak": 0,
        "release_date": "2026-07-20"
    },
    "Carnival Hunt": {
        "steam_id": 1181550,
        "metacritic_slug": "pc/carnival-hunt",
        "opencritic_id": 0,
        "opencritic_slug": "carnival-hunt",
        "backup_peak": 0,
        "release_date": "2026-07-23"
    },
    "G-Rebels": {
        "steam_id": 2445980,
        "metacritic_slug": "pc/g-rebels",
        "opencritic_id": 0,
        "opencritic_slug": "g-rebels",
        "backup_peak": 0,
        "release_date": "2026-07-20"
    },
    "Corsair Cove": {
        "steam_id": 1368140,
        "metacritic_slug": "pc/corsair-cove",
        "opencritic_id": 0,
        "opencritic_slug": "corsair-cove",
        "backup_peak": 0,
        "release_date": "2026-07-31"
    },
    "Planet Crafter": {
        "steam_id": 0,  
        "metacritic_slug": "playstation-5/the-planet-crafter",
        "opencritic_id": 16555,
        "opencritic_slug": "the-planet-crafter",
        "backup_peak": 0,
        "release_date": "2026-07-21"
    },
    "Tears of Metal": {
        "steam_id": 1913120,
        "metacritic_slug": "pc/tears-of-metal",
        "opencritic_id": 0,
        "opencritic_slug": "tears-of-metal",
        "backup_peak": 0,
        "release_date": "2026-07-22"
    },
    # -------------------------------------------------------------------------
    # UPCOMING RELEASES (ADDED LATE JULY 2026)
    # -------------------------------------------------------------------------
    "Beast of Reincarnation (Game Pass)": {
        "steam_id": 2001760,
        "metacritic_slug": "pc/beast-of-reincarnation",
        "opencritic_id": 0,
        "opencritic_slug": "beast-of-reincarnation",
        "backup_peak": 0
    },
    "Big Walk": {
        "steam_id": 1478500,
        "metacritic_slug": "pc/big-walk",
        "opencritic_id": 0,
        "opencritic_slug": "big-walk",
        "backup_peak": 0,
        "release_date": "2026-08-04"
    },
    "Akatori": {
        "steam_id": 1442520,
        "metacritic_slug": "pc/akatori",
        "opencritic_id": 0,
        "opencritic_slug": "akatori",
        "backup_peak": 0,
        "release_date": "2026-08-05"
    },
    "Marvel Tokon: Fighting Souls": {
        "steam_id": 0,
        "metacritic_slug": "playstation-5/marvel-tokon-fighting-souls",
        "opencritic_id": 0,
        "opencritic_slug": "marvel-tokon-fighting-souls",
        "backup_peak": 0,
        "release_date": "2026-08-06"
    },
    "Iron Nest: Heavy Turest Simulator": {
        "steam_id": 2950790,
        "metacritic_slug": "pc/iron-nest-heavy-turret-simulator",
        "opencritic_id": 0,
        "opencritic_slug": "iron-nest-heavy-turret-simulator",
        "backup_peak": 0,
        "release_date": "2026-08-06"
    },
    "Agent 64: Spies Never Die": {
        "steam_id": 1574480,
        "metacritic_slug": "pc/agent-64-spies-never-die",
        "opencritic_id": 0,
        "opencritic_slug": "agent-64-spies-never-die",
        "backup_peak": 0,
        "release_date": "2026-08-11"
    },
    "Riftstorm (Early Access)": {
        "steam_id": 2282790,
        "metacritic_slug": "pc/riftstorm",
        "opencritic_id": 0,
        "opencritic_slug": "riftstorm",
        "backup_peak": 0,
        "release_date": "2026-08-11"
    },
    "Security 51": {
        "steam_id": 4246860,
        "metacritic_slug": "pc/security-51",
        "opencritic_id": 0,
        "opencritic_slug": "security-51",
        "backup_peak": 0
    },
    "Pax Autocratica (Early Access)": {
        "steam_id": 1067360,
        "metacritic_slug": "pc/pax-autocratica",
        "opencritic_id": 0,
        "opencritic_slug": "pax-autocratica",
        "backup_peak": 0,
        "release_date": "2026-08-10"
    },
    "Duskfade": {
        "steam_id": 2542020,
        "metacritic_slug": "pc/duskfade",
        "opencritic_id": 0,
        "opencritic_slug": "duskfade",
        "backup_peak": 0,
        "release_date": "2026-08-13"
    },
    "Madden NFL 27": {
        "steam_id": 3940610,
        "metacritic_slug": "pc/ea-sports-madden-nfl-27",
        "opencritic_id": 0,
        "opencritic_slug": "madden-nfl-27",
        "backup_peak": 0,
        "release_date": "2026-08-13"
    },
    "Agefield High: Rock the School": {
        "steam_id": 3562580,
        "metacritic_slug": "pc/agefield-high-rock-the-school",
        "opencritic_id": 0,
        "opencritic_slug": "agefield-high-rock-the-school",
        "backup_peak": 0,
        "release_date": "2026-08-12"
    },
    "Sandustry (Game Pass)": {
        "steam_id": 2764460,
        "metacritic_slug": "pc/sandustry",
        "opencritic_id": 0,
        "opencritic_slug": "sandustry",
        "backup_peak": 0,
        "release_date": "2026-08-13"
    },
    "Mafia: Muž cti DLC": {
        "steam_id": 0,
        "metacritic_slug": "pc/mafia-the-old-country-man-of-honor",
        "opencritic_id": 0,
        "opencritic_slug": "mafia-the-old-country-man-of-honor",
        "backup_peak": 0,
        "release_date": "2026-08-14"
    },
    "Expeditions: Samurai": {
        "steam_id": 2212910,
        "metacritic_slug": "pc/expeditions-samurai",
        "opencritic_id": 0,
        "opencritic_slug": "expeditions-samurai",
        "backup_peak": 0,
        "release_date": "2026-08-07"
    },
    "Grounded 2 (PS5)": {
        "steam_id": 0,
        "metacritic_slug": "playstation-5/grounded-2",
        "opencritic_id": 0,
        "opencritic_slug": "grounded-2",
        "backup_peak": 0,
        "release_date": "2026-08-11"
    },
    "Defender of the Crown: The Legend Returns": {
        "steam_id": 4208140,
        "metacritic_slug": "pc/defender-of-the-crown-the-legend-returns",
        "opencritic_id": 0,
        "opencritic_slug": "defender-of-the-crown-the-legend-returns",
        "backup_peak": 0,
        "release_date": "2026-08-13"
    },
    "Hell let loose - Vietnam": {
        "steam_id": 3079210,
        "metacritic_slug": "pc/hell-let-loose-vietnam",
        "opencritic_id": 0,
        "opencritic_slug": "hell-let-loose-vietnam",
        "backup_peak": 0,
        "release_date": "2026-08-13"
    }
}