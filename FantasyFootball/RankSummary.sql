DROP VIEW RankSummary
GO

CREATE VIEW RankSummary AS 
select gw.Description
	,t1.Code as AwayTeam
	,t2.Code as HomeTeam
	--,oltr1.RankNumber as AwayOffensiveLineRank
	--,otr1.RankNumber as AwayOffensiveRank
	--,dtr1.RankNumber as AwayDefensiveRank
	--,oltr2.RankNumber as HomeOffensiveLineRank
	--,otr2.RankNumber as HomeOffensiveRank
	--,dtr2.RankNumber as HomeDefensiveRank
    -- TE
        --60%
            -- 50% bad defense, 25% good offensive line, 25% good offense
        --40% opponent has bad defense
    ,(0.60*(+0.5*(32-dtr1.RankNumber+1)+0.25*(oltr1.RankNumber)+0.25*(otr1.RankNumber))+ 0.40*((32-dtr2.RankNumber+1))) as TE_AwayRank 
    ,(0.60*(+0.5*(32-dtr2.RankNumber+1)+0.25*(oltr2.RankNumber)+0.25*(otr2.RankNumber))+ 0.40*((32-dtr1.RankNumber+1))) as TE_HomeRank
    -- wr
        --60%
            -- 50% bad defense, 25% good offensive line, 25% good offense
        --40% opponent has bad defense
    ,(0.60*(+0.5*(32-dtr1.RankNumber+1)+0.25*(oltr1.RankNumber)+0.25*(otr1.RankNumber))+ 0.40*((32-dtr2.RankNumber+1))) as WR_AwayRank 
    ,(0.60*(+0.5*(32-dtr2.RankNumber+1)+0.25*(oltr2.RankNumber)+0.25*(otr2.RankNumber))+ 0.40*((32-dtr1.RankNumber+1))) as WR_HomeRank
    -- rb
        --45%
            -- 75% good offensive line, 25% good defense
        --20% good offense
        --35% opponent has bad defense
    ,(0.45*(0.75*(oltr1.RankNumber)+0.25*(dtr1.RankNumber))+ 0.20*(otr1.RankNumber)+ 0.35*(dtr2.RankNumber)) as RB_AwayRank
    ,(0.45*(0.75*(oltr2.RankNumber)+0.25*(dtr2.RankNumber))+ 0.20*(otr2.RankNumber)+ 0.35*(dtr1.RankNumber)) as RB_HomeRank
    -- kicker
        --40% bad offensive line,
        --20% good offense
        --20% good defense,
        --20% opponent good defense
    ,(0.4*(32-oltr1.RankNumber+1)+ 0.2*(otr1.RankNumber)+ 0.2*(dtr1.RankNumber)+ 0.2*(dtr2.RankNumber)) as K_AwayRank
	,(0.4*(32-oltr2.RankNumber+1)+ 0.2*(otr2.RankNumber)+ 0.2*(dtr2.RankNumber)+ 0.2*(dtr1.RankNumber)) as K_HomeRank
    --defense 
        -- 40% bad opponent offense
        -- 20% good defense
        -- 40% bad opponent offensive line
    ,(0.4*(32-otr2.RankNumber+1)+ 0.2*(dtr1.RankNumber)+ 0.4*(32-oltr2.RankNumber+1)) as DEF_AwayRank
    ,(0.4*(32-otr1.RankNumber+1)+ 0.2*(dtr2.RankNumber)+ 0.4*(32-oltr1.RankNumber+1)) as DEF_HomeRank
    --offense
        -- 40% bad opponent defense
        -- 20% good offense
        -- 40% good offensive line
    ,(0.4*(32-dtr2.RankNumber+1)+ 0.2*(otr1.RankNumber)+ 0.4*(oltr1.RankNumber)) as OFF_AwayRank
    ,(0.4*(32-dtr1.RankNumber+1)+ 0.2*(otr2.RankNumber)+ 0.4*(oltr2.RankNumber)) as OFF_HomeRank
from dbo.GameSchedule gs
join dbo.GameWeek gw on gw.GameWeekID = gs.GameWeekID
left join dbo.Team t1 on gs.TeamID1 = t1.TeamID
left join dbo.Team t2 on gs.TeamID2 = t2.TeamID
left join dbo.OffensiveTeamRank otr1 on otr1.teamid = t1.teamid and otr1.Date = '2017-07-20'
left join dbo.OffensiveLineTeamRank oltr1 on oltr1.teamid = t1.teamid and oltr1.Date = '2017-08-06'
left join dbo.DefensiveTeamRank dtr1 on dtr1.teamid = t1.teamid and dtr1.Date = '2017-07-20'
left join dbo.OffensiveTeamRank otr2 on otr2.teamid = t2.teamid and otr2.Date = '2017-07-20'
left join dbo.OffensiveLineTeamRank oltr2 on oltr2.teamid = t2.teamid and oltr2.Date = '2017-08-06'
left join dbo.DefensiveTeamRank dtr2 on dtr2.teamid = t2.teamid and dtr2.Date = '2017-07-20'
where gw.GameWeekID >= 6
GO

select * from RankSummary