#include <sourcemod>
#include <sdktools>
#include <sdkhooks>
#include <smjansson>
#include <steamworks>
#include <d2c>

#pragma newdecls required
//# export interface PlayerInMatchDTO {
//#   readonly steam_id: string;
//#   readonly team: number;
//#   readonly kills: number;
//#   readonly deaths: number;
//#   readonly assists: number;
//#   readonly level: number;
//#   readonly items: string[];
//#   readonly gpm: number;
//#   readonly xpm: number;
//#   readonly last_hits: number;
//#   readonly denies: number;
//#
//#   readonly hero: string;
//# }
//#
//# export class GameResultsEvent {
//#   constructor(
//#     public readonly matchId: number,
//#     public readonly radiantWin: boolean,
//#     public readonly duration: number,
//#     public readonly type: MatchmakingMode,
//#     public readonly timestamp: number,
//#     public readonly server: string,
//#     public readonly players: PlayerInMatchDTO[],
//#   ) {}
//# }


int match_id;
int game_mode;
char server_url[40]
Handle teamPreset[10];

int expected_player_count = 0;

public bool PlayerInMatchJSON(Handle hObj, int index){
	char steamid[20]
	bool hasPlayer = GetSteamid(index, steamid)

	if(!hasPlayer){
		return false;
	}

	char heroName[40]
	GetHero(index, heroName)


	json_object_set_new(hObj, "hero", json_string(heroName));
	json_object_set_new(hObj, "steam_id", json_string(steamid));
	json_object_set_new(hObj, "team", json_integer( GetTeam(index) ));
	json_object_set_new(hObj, "level", json_integer( GetLevel(index) ));

	json_object_set_new(hObj, "kills", json_integer( GetKills(index) ));
	json_object_set_new(hObj, "deaths", json_integer( GetDeaths(index) ));
	json_object_set_new(hObj, "assists", json_integer( GetAssists(index) ));

	json_object_set_new(hObj, "gpm", json_integer(  GetGPM(index) ));
	json_object_set_new(hObj, "xpm", json_integer(  GetXPM(index) ));

	json_object_set_new(hObj, "last_hits", json_integer(  GetLasthits(index) ));
	json_object_set_new(hObj, "denies", json_integer( GetDenies(index) ));

	Handle hArray = json_array();

	GetItems(index, hArray)




	json_object_set_new(hObj, "items", hArray);

//	CreatePlayerIfNotExists(steamid);
//	InsertPlayerInMatch(matchId, steamid, heroName, team, kills, deaths, assists, level, items, gpm, xpm, lastHits, denies);
	return true
}

public void GenerateMatchResults(){

	int winnerTeam = GameRules_GetProp("m_nGameWinner", 4, 0);
	bool isRadiantWin = winnerTeam == 2;

	Handle obj = json_object();
	json_object_set_new(obj, "matchId", json_integer(match_id));
	json_object_set_new(obj, "radiantWin", json_boolean(isRadiantWin));
	json_object_set_new(obj, "duration", json_integer(GetDuration()));
	json_object_set_new(obj, "type", json_integer(game_mode));
	json_object_set_new(obj, "timestamp", json_integer(GetTime()));
	json_object_set_new(obj, "server", json_string(server_url));
	Handle hArray = json_array();

	int heroCount = 0;

	for (int i = 0; i <= 10; i++){
		PrintToServer("Saving for player %d", i)
		Handle pObj = json_object();
		bool good = PlayerInMatchJSON(pObj, i);
		PrintToServer("%d", good)
		if(good){
			json_array_append(hArray, pObj)
			heroCount++;
		}
	}
	if(heroCount != 2 && heroCount != 10){
		PrintToChatAll("Матч не будет сохранен: неполная игра");
		return;

	}

	json_object_set_new(obj, "players", hArray);
	char sJSON[10000];
	json_dump(obj, sJSON, sizeof(sJSON), 0);
	PrintToServer(sJSON)

	Handle request = SteamWorks_CreateHTTPRequest(k_EHTTPMethodPOST, "http://localhost:5001/match_results")
	if(request == null){
		PrintToServer("Request is null.")
		return;
	}

	SteamWorks_SetHTTPRequestRawPostBody(request, "application/json; charset=UTF-8", sJSON, strlen(sJSON));
	SteamWorks_SetHTTPRequestNetworkActivityTimeout(request, 30);
	SteamWorks_SetHTTPCallbacks(request, HTTPCompleted, HeadersReceived, HTTPDataReceive);

	SteamWorks_SendHTTPRequest(request);


}

public int HTTPCompleted(Handle request, bool failure, bool requestSuccessful, EHTTPStatusCode statuscode, any data, any data2) {
	PrintToServer("HTTP Complted")
}

public int HTTPDataReceive(Handle request, bool failure, int offset, int statuscode, any dp) {
	PrintToServer("Data received %d", statuscode)
	if(statuscode == 200){
		PrintToChatAll("Матч сохранен.")
	}
	delete request;
}

public int HeadersReceived(Handle request, bool failure, any data, any datapack) {
	PrintToServer("Headers received")
}

public void OnClientPutInServer(int client)
{

	if(!IsFakeClient(client)){
		char steamid[20];
		GetClientAuthId(client, AuthIdType:2, steamid, sizeof(steamid), true);



		PrintToServer("%s steamid", steamid);

		int team = GetTeamForSteamID(steamid)
		if(team != -1){
			ChangeClientTeam(client, team);
		}else{
			KickClient(client, "Вы не участник игры");
		}


	}
}


public Action Command_jointeam(int client, const char[] command, int args)
{
	return Plugin_Handled;
}

public void OnPluginStart()
{
	HookEvent("dota_match_done", OnMatchFinish, EventHookMode:0);
	HookEvent("game_rules_state_change", OnMatchStart, EventHookMode:0)

	AddCommandListener(Command_jointeam, "jointeam");

	LoadMatchInfo();
	AddCommandListener(Command_Say, "say");
	AddCommandListener(Command_Say, "say_team");

	CreateTimer(10.0, SetPlayersToStartGame);
}

public Action SetPlayersToStartGame(Handle timer){
	if(game_mode == GameMode_Solomid){
		SetPlayersToStart(2);
	}else{
		SetPlayersToStart(10);
	}
}

public void LoadMatchInfo(){
	char path[500];
	BuildPath(Path_SM, path, sizeof(path), "configs/match.json")
	Handle file = OpenFile(path, "r+");
	if(!file){
		PrintToServer("Can't read file... :( %s", path);
		return;
	}
	char line[10000];

	ReadFileString(file, line, sizeof(line))


	Handle hObj = json_load(line);

	match_id = json_object_get_int(hObj, "matchId");
	game_mode = json_object_get_int(hObj, "mode");
	PrintToServer("Match ID: %d", match_id);

	int i = 0;
	while (i < 10)
	{
    	/*the 2 cells of the array are as follows:
    		cell 0 - steamid
    		cell 1 - team
    	*/
		teamPreset[i] = CreateArray(100, 2);
		i++;
	}
	expected_player_count = 0;
	i = 0;

	Handle radiant = json_object_get(hObj, "radiant");
	for(int iElement = 0; iElement < json_array_size(radiant); iElement++) {
		char steamid[20];
		json_array_get_string(radiant, iElement, steamid, sizeof(steamid));
		SetArrayString(teamPreset[i], 0, steamid);
		SetArrayCell(teamPreset[i], 1, 2);
		i++;
		expected_player_count++;
	}
	Handle dire = json_object_get(hObj, "dire");

	for(int iElement = 0; iElement < json_array_size(dire); iElement++) {
		char steamid[20];
		json_array_get_string(dire, iElement, steamid, sizeof(steamid));
		SetArrayString(teamPreset[i], 0, steamid);
		SetArrayCell(teamPreset[i], 1, 3);
		i++;
		expected_player_count++;
	}

	json_object_get_string(hObj, "server_url", server_url, sizeof(server_url))

	CloseHandle(file);
}

public Action Command_Test(int args)
{
	PrintToServer("%d", match_id)
	return Plugin_Handled;
}


public void GetItems(int index, Handle items){
	int hero = GetEntPropEnt(GetPlayerResourceEntity(), Prop_Send, "m_hSelectedHero", index);


	for (int i = 0; i < 6; ++i){
		int item = GetEntPropEnt(hero, Prop_Send, "m_hItems", i);

		char classname[200];
		if (!IsValidEntity(item)){
			classname = "item_emptyitembg"
		}else{
			GetEdictClassname(item, classname, sizeof(classname));
		}

		json_array_append_new(items, json_string(classname));
	}
}


public Action Command_Say(int client, const char[] command, int argc)
{
	char sayString[32];
	GetCmdArg(1, sayString, sizeof(sayString));
	GetCmdArgString(sayString, sizeof(sayString));
	StripQuotes(sayString);
	if(!strcmp(sayString,"-save",false))
	{
		OnMatchFinished(false);
	}
}

public int GetTeamForSteamID(char steam_id[20]){
	int i = 0;
	while(i < sizeof(teamPreset)){
		char sid[20];
		GetArrayString(teamPreset[i], 0, sid, sizeof(sid))
		PrintToServer("Match? %s", sid)
		if(!strcmp(sid, steam_id, false))	{
			return GetArrayCell(teamPreset[i], 1);
		}
		i++;
	}

	return -1;
}




public Action OnMatchStart(Handle event, char[] name, bool dontBroadcast){
	int gameState = GameRules_GetProp("m_nGameState");


	if(gameState == 3){
		// HERO_SELECTION
		// check if all players are here
		if(GetPlayersCount() < expected_player_count){
			// not enough players
		}
	}
}

public Action OnMatchFinish(Handle event, char[] name, bool dontBroadcast){
	OnMatchFinished(true);
}

public void OnMatchFinished(bool shutdown){

	if(shutdown){
		CreateTimer(60.0, Shutdown);
		PrintToChatAll("Сервер отключится через минуту");
	}
	GenerateMatchResults();
}

public Action Shutdown(Handle timer)
{
	ServerCommand("exit");
}