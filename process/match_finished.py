
# export interface PlayerInMatchDTO {
#   readonly steam_id: string;
#   readonly team: number;
#   readonly kills: number;
#   readonly deaths: number;
#   readonly assists: number;
#   readonly level: number;
#   readonly items: string[];
#   readonly gpm: number;
#   readonly xpm: number;
#   readonly last_hits: number;
#   readonly denies: number;
#
#   readonly hero: string;
# }
#
# export class GameResultsEvent {
#   constructor(
#     public readonly matchId: number,
#     public readonly radiantWin: boolean,
#     public readonly duration: number,
#     public readonly type: MatchmakingMode,
#     public readonly timestamp: number,
#     public readonly server: string,
#     public readonly players: PlayerInMatchDTO[],
#   ) {}
# }

# todo: move to server and handle from plugin
