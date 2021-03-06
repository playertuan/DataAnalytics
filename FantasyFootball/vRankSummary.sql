DROP VIEW vRankSummary
GO

CREATE VIEW vRankSummary AS 
select gs.GameWeek
	,gs.AwayTeam
	,gs.HomeTeam
    -- TE
        --60%
            -- 50% bad defense, 25% good offensive line, 25% good offense
        --40% opponent has bad defense
    ,(0.60*(+0.5*(32-dtr1.[Rank]+1)+0.25*(olr1.[Rank])+0.25*(otr1.[Rank]))+ 0.40*((32-dtr2.[Rank]+1))) as TE_AwayRank 
    ,(0.60*(+0.5*(32-dtr2.[Rank]+1)+0.25*(olr2.[Rank])+0.25*(otr2.[Rank]))+ 0.40*((32-dtr1.[Rank]+1))) as TE_HomeRank
    -- wr
        --60%
            -- 50% bad defense, 25% good offensive line, 25% good offense
        --40% opponent has bad defense
    ,(0.60*(+0.5*(32-dtr1.[Rank]+1)+0.25*(olr1.[Rank])+0.25*(otr1.[Rank]))+ 0.40*((32-dtr2.[Rank]+1))) as WR_AwayRank 
    ,(0.60*(+0.5*(32-dtr2.[Rank]+1)+0.25*(olr2.[Rank])+0.25*(otr2.[Rank]))+ 0.40*((32-dtr1.[Rank]+1))) as WR_HomeRank
    -- rb
        --45%
            -- 75% good offensive line, 25% good defense
        --20% good offense
        --35% opponent has bad defense
    ,(0.45*(0.75*(olr1.[Rank])+0.25*(dtr1.[Rank]))+ 0.20*(otr1.[Rank])+ 0.35*(32-dtr2.[Rank])) as RB_AwayRank
    ,(0.45*(0.75*(olr2.[Rank])+0.25*(dtr2.[Rank]))+ 0.20*(otr2.[Rank])+ 0.35*(32-dtr1.[Rank])) as RB_HomeRank
    -- kicker
        --40% bad offensive line,
        --20% good offense
        --20% good defense,
        --20% opponent good defense
    ,(0.4*(32-olr1.[Rank]+1)+ 0.2*(otr1.[Rank])+ 0.2*(dtr1.[Rank])+ 0.2*(dtr2.[Rank])) as K_AwayRank
	,(0.4*(32-olr2.[Rank]+1)+ 0.2*(otr2.[Rank])+ 0.2*(dtr2.[Rank])+ 0.2*(dtr1.[Rank])) as K_HomeRank
    --defense
        -- 40% bad opponent offense
        -- 20% good defense
        -- 40% bad opponent offensive line
    ,(0.4*(32-otr2.[Rank]+1)+ 0.2*(dtr1.[Rank])+ 0.4*(32-olr2.[Rank]+1)) as DEF_AwayRank
    ,(0.4*(32-otr1.[Rank]+1)+ 0.2*(dtr2.[Rank])+ 0.4*(32-olr1.[Rank]+1)) as DEF_HomeRank
    --offense used for the QB
        -- 40% bad opponent defense
        -- 20% good offense
        -- 40% good offensive line
    ,(0.4*(32-dtr2.[Rank]+1)+ 0.2*(otr1.[Rank])+ 0.4*(olr1.[Rank])) as OFF_AwayRank
    ,(0.4*(32-dtr1.[Rank]+1)+ 0.2*(otr2.[Rank])+ 0.4*(olr2.[Rank])) as OFF_HomeRank
from dbo.GameSchedule gs
left join dbo.OffensiveTeamRank otr1 on otr1.Team = gs.AwayTeam
left join dbo.OffensiveLineRank olr1 on olr1.Team = gs.AwayTeam
left join dbo.DefensiveTeamRank dtr1 on dtr1.Team = gs.AwayTeam
left join dbo.OffensiveTeamRank otr2 on otr2.Team = gs.HomeTeam
left join dbo.OffensiveLineRank olr2 on olr2.Team = gs.HomeTeam
left join dbo.DefensiveTeamRank dtr2 on dtr2.Team = gs.HomeTeam
GO

select * from vRankSummary