#if defined _d2c_helpers
 #endinput
#endif
#define _d2c_helpers

#include <sourcemod>
#include <sdktools>
#include <sdkhooks>
#include <smjansson>
#include <steamworks>



enum GameMode 
{ 
	GameMode_Ranked = 0,
	GameMode_Unranked = 1,
	GameMode_Solomid = 2,
	GameMode_Diretide = 3,
	GameMode_Greeviling = 4,
	GameMode_AbilityDraft = 5,
}

public GetIntProperty(index, String:prop[]){
	return GetEntProp(GetPlayerResourceEntity(), Prop_Send, prop, 4, index)
}


public GetDuration(){
	new non_game_time = RoundFloat(GameRules_GetPropFloat("m_flGameStartTime"))
	PrintToServer("%d", non_game_time)
	new total_time = RoundFloat(GameRules_GetPropFloat("m_fGameTime"))
	return total_time - non_game_time;
}


public GetXPM(index){
	new totalEarned = GetIntProperty(index, "m_iTotalEarnedXP")
	return totalEarned / RoundFloat(GameRules_GetPropFloat("m_fGameTime") / 60)
}

public GetGPM(index){
	new totalEarned = GetIntProperty(index, "m_iTotalEarnedGold")
	return totalEarned / RoundFloat(GameRules_GetPropFloat("m_fGameTime") / 60)
}


public GetDenies(index){
	return GetIntProperty(index, "m_iDenyCount");
}

public GetLasthits(index){
	return GetIntProperty(index, "m_iLastHitCount");
}

public GetLevel(index){
	return GetIntProperty(index, "m_iLevel");
}

public GetTeam(index){
	return GetIntProperty(index, "m_iPlayerTeams");
}

public GetKills(index){
	return GetIntProperty(index, "m_iKills");
}

public GetDeaths(index){
	return GetIntProperty(index, "m_iDeaths");
}

public GetAssists(index){
	return GetIntProperty(index, "m_iAssists");
}

public GetHero(index, String:buffer[40]){
	new heroEntity = GetEntPropEnt(GetPlayerResourceEntity(), Prop_Send, "m_hSelectedHero", index);
	GetEntityClassname(heroEntity, buffer, sizeof(buffer));
}

public bool GetSteamid(index, String:buffer[20]){
	new offset = FindSendPropInfo("CDOTA_PlayerResource", "m_iPlayerSteamIDs");
	new sid = GetEntData(GetPlayerResourceEntity(), offset + index * 8, 4);
	if(sid == 0) return false
	
	Format(buffer, sizeof(buffer), "[U:1:%d]", sid)
	return true
}

public GetPlayersCount(){
	new heroCount = 0;
	
	for (new i = 0; i <= 10; i++){
		new String:steamid[20]
		new hasPlayer = GetSteamid(i, steamid)
		
		if(hasPlayer){
			heroCount++;
		}
	} 
	
	return heroCount;
}

public SetPlayersToStart(int toStart)
{
    ServerCommand("dota_wait_for_players_to_load_count %d", toStart);
    PrintToServer("Server command executed(wait for load count)");
}
