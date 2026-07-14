#pragma endian little
import type.base;

enum CourseID : u32 {
    MARIO_CIRCUIT = 0,
    ROCK_ROCK_MOUNTAIN = 1,
    CHEEP_CHEEP_LAGOON = 2,
    DAISY_HILLS = 3,
    TOAD_CIRCUIT = 4,
    SHY_GUY_BAZAAR = 5,
    NEO_BOWSER_CITY = 6,
    DK_JUNGLE = 7,
    WUHU_LOOP = 8,
    MAKA_WUHU = 9,
    ROSALINA_ICE_WORLD = 10,
    BOWSER_CASTLE = 11,
    PIRANHA_PLANT_SLIDE = 12,
    RAINBOW_ROAD = 13,
    WARIO_SHIPYARD = 14,
    MUSIC_PARK = 15,
    WII_COCONUT_MALL = 16,
    WII_KOOPA_CAPE = 17,
    WII_MAPLE_TREEWAY = 18,
    WII_MUSHROOM_GORGE = 19,
    DS_LUIGI_MANSION = 20,
    DS_AIRSHIP_FORTRESS = 21,
    DS_DK_PASS = 22,
    DS_WALUIGI_PINBALL = 23,
    GCN_DINO_DINO_JUNGLE = 24,
    GCN_DAISY_CRUISER = 25,
    N64_LUIGI_RACEWAY = 26,
    N64_KALIMARI_DESERT = 27,
    N64_KOOPA_BEACH = 28,
    GBA_BOWSER_CASTLE_1 = 29,
    SNES_MARIO_CIRCUIT_2 = 30,
    SNES_RAINBOW_ROAD = 31,
    WUHU_TOWN = 32,
    HONEYBEE_HIVE = 33,
    SHERBET_RINK = 34,
    DS_PALM_SHORE = 35,
    N64_BIG_DONUT = 36,
    GBA_BATTLE_COURSE_1 = 37,
    WINNING_RUN = 38,
    TEST = 39,
    RANDOM = 40,
    COURSE_MAX = 41
};

enum RaceLogSaveDataFlags : u8 {
    FLAG_1 = 1,
    FLAG_2 = 2,
    ROCKET_START_SUCCESSFULL = 4
};

enum PlayerDataFlags : u8 {
    COUNTRY_SET_TO_VISIBLE = 1,
    ONLINE_STATUS_VISIBLE = 2,
    GOLD_WHEEL_UNLOCKED = 4,
    RANK_3_STARS = 8,
    RANK_2_STARS = 16,
    RANK_1_STAR = 32
};

enum GrandPrixRecord4Bytes : u32 {
    NO_RANK = 0,
    A = 1,
    B = 2,
    C = 3,
    ONE_STAR = 4,
    TWO_STARS = 5,
    THREE_STARS = 6
};

struct PlayerID {
    type::Hex<u64> transferableId;
    type::Hex<u32> field1_0x8;
    type::Hex<u32> field2_0xc;
};

struct struct_68 {
    u8 field0_0x0;
    u8 field1_0x1;
    u8 field2_0x2;
    u8 field3_0x3;
};

union union_1 {
    u32 flags;
    u32 vr;
    GrandPrixRecord4Bytes gpRecord;
    struct_68 field3;
};

struct CFLStoreData {
    u8 data[96];
};

struct FlagData {
    u16 numGPPerCourse[32];
    u16 numLocalMultiplayerGPPerCourse[32];
    u16 numTimesUsed_Driver_GP[18];
    u16 numTimesUsed_Body_GP[17];
    u16 numTimesUsed_Tire_GP[10];
    u16 numTimesUsed_Wing_GP[7];
    u32 gpNumLocalMultiplayerHumanPlayers;
    u16 numLocalMultiplayerVSPerCourse[32];
    u16 numOnlineVSPerCourse[32];
    u16 numTimesUsed_Driver_VS[18];
    u16 numTimesUsed_Body_VS[17];
    u16 numTimesUsed_Tire_VS[10];
    u16 numTimesUsed_Wing_VS[7];
    u32 vsNumLocalMultiplayerPlayers;
    u32 vsNumLocalMultiplayerHumanPlayers;
    s32 vsNumOnlineHumanPlayers;
    s32 vsDisconnectedNum;
    u32 field17_0x1e4;
    u16 numCoinRunnersPerCourse[6];
    u16 numBalloonBattlesPerCourse[6];
    u16 numOnlineBattlesPerCourse[6];
    u16 numLocalMultiplayerBattlesPerCourse[6];
    u16 numTimesUsed_Driver_Battle[18];
    u16 numTimesUsed_Body_Battle[17];
    u16 numTimesUsed_Tire_Battle[10];
    u16 numTimesUsed_Wing_Battle[7];
    u32 battleNumLocalMultiplayerPlayers;
    u32 battleNumLocalMultiplayerHumanPlayers;
    s32 battleNumOnlineHumanPlayers;
    s32 battleDisconnectedNum;
    s32 field30_0x290;
    u16 numTimeTrialsPerCourse[32];
    u16 field32_0x2d4;
    u16 field33_0x2d6;
    u16 field34_0x2d8;
    u16 numTimesUsed_Driver_TimeTrial[18];
    u16 numTimesUsed_Body_TimeTrial[17];
    u16 numTimesUsed_Tire_TimeTrial[10];
    u16 numTimesUsed_Wing_TimeTrial[7];
    u8 field39_0x342;
    u8 field40_0x343;
    u32 numRacesPlayed;
    s32 raceTime;
    s32 raceTimeInFirstPerson;
    s32 flying;
    s32 underwater;
    u32 coins;
    s32 numStartDriftJump;
    s32 numTricks;
    s32 numDriftStart;
    s32 driftTime;
    s32 numMiniturboLevel1;
    s32 numMiniturboLevel2;
    u32 popBalloon;
    u32 numLoseBalloon;
    u32 numStolenBalloon;
    s32 numObtainCoin;
    s32 numDroppedCoin;
    u32 numCoinsPerCourse[32];
    u32 numRespawnsPerVSCourse[32];
    u32 numRespawnsPerBattleCourse[6];
    u16 obtainItem[20];
    u16 usedItemFromSlot[20];
    u16 numThrowItem[10];
    u32 field64_0x504;
    u32 field65_0x508;
    u32 field66_0x50c;
    s32 numHoldItem[10];
    u32 field68_0x538;
    u32 field69_0x53c;
    u32 field70_0x540;
    u32 field71_0x544;
    u32 field72_0x548;
    u32 field73_0x54c;
    u32 field74_0x550;
    u32 streetpassTags;
    u32 numDisconnectedRaces;
    u8 field77_0x55c;
    u8 field78_0x55d;
    u8 field79_0x55e;
    u8 field80_0x55f;
    u32 vr;
    u32 wins;
    u32 losses;
    u32 field84_0x56c;
    u8 field85_0x570;
    u8 field86_0x571;
    u16 field87_0x572;
    u16 field88_0x574;
    u16 field89_0x576;
    u16 field90_0x578;
    u16 field91_0x57a;
    u16 field92_0x57c;
    u16 field93_0x57e;
    u16 field94_0x580;
    u16 field95_0x582;
    u16 field96_0x584;
    u8 unlockCoinNumberArrayIdx;
    u8 field98_0x587;
    u32 field99_0x588;
    u32 field100_0x58c;
    u8 percentagesOfRacesPlayedWithGyro[100];
};

struct PlayerDataNoMii {
    union_1 data;
    u32 wins;
    u32 losses;
    s32 field3_0xc;
    s32 field4_0x10;
    u16 driver;
    u16 body;
    u16 tire;
    u16 wing;
    type::Hex<u32> field9_0x1c;
    PlayerID playerId;
    s32 myPrincipalId;
    s16 country;
    s16 latitude;
    s16 longitude;
    u8 region;
    PlayerDataFlags flags;
};

struct PlayerData {
	PlayerDataNoMii base;
	CFLStoreData mii;
	bool playerDataFilled;
	u8 field_0x9d[3];
};

struct OpponentData {
	type::Hex<s32> field_0x00;
	u8 field_0x04[4];
	PlayerData playerData;
};

struct RankingData {
    u32 data1;
    u32 data2;
};

struct RankingRow {
    RankingData entry[6];
};

struct RankingSaveData {
    u8 field_0x00[0x600];
};

struct RaceLogSaveData {
    s32 holdItemTime;
    s32 raceTime;
    s32 driftTime;
    s32 raceTimeInFirstPlace;
    u32 raceTimeInFirstPerson;
    s16 driftStart;
    u16 bumpIntoEnemy;
    s16 startDriftJump;
    u16 trick;
    s16 miniturbos;
    s16 respawns;
    s16 numEnemiesHitWithItems;
    u8 rankUpWhileFlying;
    u8 rankUpWhileUnderwater;
    u16 usedItemAndHitSomeone_Shell;
    u16 throwItem_Shell;
    u16 usedItemAndHitSomeone_Banana;
    u16 throwItem_Banana;
    u16 usedItemAndHitSomeone_BobOmb;
    u16 throwItem_BobOmb;
    RaceLogSaveDataFlags flags;
    u8 field21_0x31;
    u16 field22_0x32;
};

struct PlayerFlagSaveData {
    FlagData flagData;
    RaceLogSaveData racelogSaveData[10];
    u8 field2_0x7fc;
    u8 field3_0x7fd;
    u8 numRacesBeforeUpdatingTitleType;
    u8 field5_0x7ff;
};

struct SystemSaveDataNoChecksum {
    char magic[4];
    s16 field1_0x4;
    u16 field2_0x6;
    CFLStoreData mii;
    PlayerID playerId;
    char16 cecComment[17];
	u8 field_0x9a[78];
    CourseID lastPlayedTimeTrialCourse;
    u8 field85_0xec;
    u8 field86_0xed;
    u8 field87_0xee;
    u8 field88_0xef;
    type::Hex<s32> field89_0xf0;
    type::Hex<s32> field90_0xf4;
    u32 lastUploadPlayerLogTime;
    u32 spotPassDownloadedGhostCourseFlags;
    s32 field93_0x100;
    u32 ghostUpdateBitflag;
    s32 field95_0x108;
    RankingSaveData rankingSaveData;
    u8 grandPrixData[32];
    u8 field98_0x72c;
    u8 field99_0x72d;
    u8 field100_0x72e;
    u8 field101_0x72f;
    OpponentData opponentList[100];
    PlayerFlagSaveData playerFlagSaveData;
};

struct SystemSaveData {
    SystemSaveDataNoChecksum data;
    type::Hex<u32> crc32;
};

SystemSaveData save @ 0x00;