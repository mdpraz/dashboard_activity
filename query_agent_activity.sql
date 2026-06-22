-- ============================================================
-- Agent Activity Dashboard — Query Generator
-- Database : PostgreSQL
-- Output   : 1 baris per (grass_date, team_id, segment, campaign, teleid)
-- 
-- Hierarki:  segment → campaign → agent
-- Contoh:    dropoff → PROVIDER_NETWORK_1 → tele032
--
-- Export: Jalankan di DBeaver/psql → export CSV → paste ke Google Sheet
-- ============================================================

with base_tele as (
    select
        date_trunc('day', import_time)::date   as import_date
        ,date_trunc('day', call_time)::date    as call_date

        -- segment: kategori besar (dropoff, risk, h5_approved, telkomsel, ...)
        ,case
            when product_name ilike '%ACQUISITION_PROVIDER_NETWORK_1 %'         then 'dropoff'
            when product_name ilike '%ACQUISITION_H5 %'                          then 'h5_approved'
            when product_name ilike '%ACQUISITION_H5_DROPOFF_HISTORY %'         then 'h5_approved'
            when product_name ilike '%ACQUISITION_CTBU %'                        then 'dropoff'
            when product_name ilike '%ACQUISITION_PRIMEA %'                      then 'dropoff'
            when product_name ilike '%ACQUISITION_NEVER_APPLY %'                 then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_1 %'             then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_2 %'             then 'megacc_point'
            when product_name ilike '%ACQUISITION_PRIMEB %'                      then 'dropoff'
            when product_name ilike '%ACQUISITION_V1 %'                          then 'risk'
            when product_name ilike '%ACQUISITION_PRIMEA_T2_NEW_MODEL %'        then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC %'                      then 'dropoff'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_1 %'    then 'megacc_point'
            when product_name ilike '%ACQUISITION_PRIMEA_ANA %'                  then 'risk'
            when product_name ilike '%ACQUISITION_H5_HISTORY %'                  then 'h5_approved'
            when product_name ilike '%ACQUISITION_PRIMEA_T0_NEW_MODEL %'        then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_SPM %'                   then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_1_B %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_PRIME_MODELLING_HOT_1 %'     then 'risk'
            when product_name ilike '%ACQUISITION_PRIMEA_ANA_RECYCLE %'         then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_HIGHLY_APPROVED %'      then 'risk'
            when product_name ilike '%ACQUISITION_V2 %'                          then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_1_A %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_V1_B %'                        then 'risk'
            when product_name ilike '%ACQUISITION_V1_A %'                        then 'risk'
            when product_name ilike '%ACQUISITION_ANA_PARTNERSHIP %'             then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_MODELLING_COLD_2 %'    then 'risk'
            when product_name ilike '%ACQUISITION_V3_A %'                        then 'risk'
            when product_name ilike '%ACQUISITION_HIGHLY_APPROVED_WHITELIST %'  then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_MODELLING_COLD_1 %'    then 'risk'
            when product_name ilike '%ACQUISITION_H5_HISTORY_1 %'               then 'h5_approved'
            when product_name ilike '%ACQUISITION_PRIME_MODELLING_HOT_2 %'     then 'risk'
            when product_name ilike '%ACQUISITION_V2_A %'                        then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_2_A %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_A %'    then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_2_B %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_B %'    then 'megacc_point'
            when product_name ilike '%ACQUISITION_V2_B %'                        then 'risk'
            when product_name ilike '%ACQUISITION_V3_B %'                        then 'risk'
            when product_name ilike '%ACQUISITION_V4 %'                          then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_MODELLING %'             then 'risk'
            when product_name ilike '%ACQUISITION_PRIMEA_T1_NEW_MODEL %'        then 'risk'
            when product_name ilike '%ACQUISITION_HIGH_PRIME_RECENTLY %'        then 'risk'
            when product_name ilike '%ACQUISITION_V3 %'                          then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_HIGH_APPLY %'           then 'risk'
            when product_name ilike '%ACQUISITION_TWICE_APPLY %'                 then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_1_C %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_HIGH_APPLY %'   then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_HIGH_APPLY_C %' then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_2 %'    then 'megacc_point'
            when product_name ilike '%ACQUISITION_PRIME_TESTING_2 %'            then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_TESTING_1 %'            then 'risk'
            when product_name ilike '%ACQUISITION_RETRY_APPLY %'                 then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_ALLO_CARE_1 %'         then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_2_C %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_PRIME_ANTIFRAUD %'            then 'risk'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_3_C %'  then 'megacc_point'
            when product_name ilike '%ACQUISITION_MEGACC_POINT_RECYCLE_3 %'    then 'megacc_point'
            when product_name ilike '%ACQUISITION_PRIME_LIQUIDITY %'            then 'risk'
            when product_name ilike '%ACQUISITION_PRIMEA_NEW_MODEL %'           then 'risk'
            when product_name ilike '%ACQUISITION_NEW_PRIME_PRIORITY %'         then 'risk'
            when product_name ilike '%ACQUISITION_PRIME_MERCHANT %'             then 'risk'
            when product_name ilike '%ACQUISITION_PRIMEB_HIGH_APPLY %'          then 'risk'
            when product_name ilike '%ACQUISITION_PRIMEA_HIGH_APPLY %'          then 'risk'
            when product_name ilike '%ACQUISITION_HISTORICAL_DROPOFF %'         then 'risk'
            when product_name ilike '%ACQUISITION_TELKOMSEL_CC_USER %'          then 'telkomsel'
            when product_name ilike '%ACQUISITION_TELKOMSEL_MODELLING %'        then 'telkomsel'
            when product_name ilike '%ACQUISITION_TELKOMSEL_MSIGHT_CASHLESS %'  then 'telkomsel'
            when product_name ilike '%ACQUISITION_TELKOMSEL_POSTPAID %'         then 'telkomsel'
            else lower(split_part(product_name, '_', 1))
        end as segment

        -- campaign: nama produk bersih, buang prefix "ACQUISITION_" dan suffix " (N) DDMMYYYY"
        -- contoh: "ACQUISITION_PROVIDER_NETWORK_1 (1) 22062026" → "PROVIDER_NETWORK_1"
        ,trim(split_part(
            regexp_replace(product_name, '^ACQUISITION_', '', 'i'),
            ' ', 1
        )) as campaign

        ,teleid_call          as teleid
        ,agent_call
        ,cust_phone
        ,call_time
        ,contact_time
        ,contact_duration
        ,import_time
    from datamarts_dm_telemarketing_user_acq
    where import_time::date between date_trunc('day', current_date - interval '14' day)::date
                                and current_date
        and (
            call_time is null
            or call_time::date >= (import_time::date - interval '30' day)
        )
)

,team_base as (
    select
        basnm      as agent_name
        ,frndeptid as team_id
    from d3_sys_staff
)

,base as (
    select
        b.team_id
        ,a.*
    from base_tele a
    left join team_base b on a.agent_call = b.agent_name
)

,dominant_campaign as (
    -- campaign dominan per agen per hari: campaign dengan leads terbanyak
    select
        call_date
        ,agent_call
        ,segment
        ,campaign
        ,count(distinct cust_phone) as leads_cnt
        ,row_number() over (
            partition by call_date, agent_call
            order by count(distinct cust_phone) desc
        ) as rn
    from base
    where call_date is not null
    group by 1, 2, 3, 4
)

select
    -- ── Dimensi ──────────────────────────────────────────────────────────
    b.call_date                                                         as grass_date
    ,b.team_id
    ,d.segment
    ,d.campaign
    ,b.teleid

    -- ── Leads & waktu kerja ──────────────────────────────────────────────
    ,count(distinct case when b.import_date = b.call_date
                         then b.cust_phone end)                         as leads_assign
    ,to_char(min(b.call_time), 'HH24:MI')                              as start_call
    ,to_char(max(b.call_time), 'HH24:MI')                              as end_call
    ,round(extract(epoch from (max(b.call_time) - min(b.call_time)))
           / 3600.0, 2)                                                 as hours_work

    -- ── Talk time (raw, dihitung ulang di Python jadi talk_hours) ────────
    ,sum(b.contact_duration)                                            as contact_duration

    -- ── Volume keseluruhan ───────────────────────────────────────────────
    ,count(case when b.call_time    is not null then 1 end)             as calls
    ,count(case when b.contact_time is not null then 1 end)             as contacts
    ,count(distinct case when b.contact_duration >= 5
                         then b.cust_phone end)                         as unique_contacts
    ,count(case when b.contact_duration >= 30 then 1 end)               as contacts_30s
    ,sum(case when b.contact_duration >= 30
              then b.contact_duration end)                              as contact_duration_30s

    -- ── Slot 08:00–10:00 ─────────────────────────────────────────────────
    ,count(case when extract(hour from b.call_time) between 8 and 9
                 and b.call_time    is not null then 1 end)             as calls_0810
    ,count(case when extract(hour from b.call_time) between 8 and 9
                 and b.contact_time is not null then 1 end)             as contacts_0810
    ,count(distinct case when extract(hour from b.call_time) between 8 and 9
                          and b.contact_duration >= 5
                          then b.cust_phone end)                        as unique_contacts_0810
    ,count(case when extract(hour from b.call_time) between 8 and 9
                 and b.contact_duration >= 30 then 1 end)               as contacts_30s_0810
    ,sum(case when extract(hour from b.call_time) between 8 and 9
               and b.contact_duration >= 30
               then b.contact_duration end)                             as contact_duration_30s_0810

    -- ── Slot 10:00–12:00 ─────────────────────────────────────────────────
    ,count(case when extract(hour from b.call_time) between 10 and 11
                 and b.call_time    is not null then 1 end)             as calls_1012
    ,count(case when extract(hour from b.call_time) between 10 and 11
                 and b.contact_time is not null then 1 end)             as contacts_1012
    ,count(distinct case when extract(hour from b.call_time) between 10 and 11
                          and b.contact_duration >= 5
                          then b.cust_phone end)                        as unique_contacts_1012
    ,count(case when extract(hour from b.call_time) between 10 and 11
                 and b.contact_duration >= 30 then 1 end)               as contacts_30s_1012
    ,sum(case when extract(hour from b.call_time) between 10 and 11
               and b.contact_duration >= 30
               then b.contact_duration end)                             as contact_duration_30s_1012

    -- ── Slot 12:00–14:00 ─────────────────────────────────────────────────
    ,count(case when extract(hour from b.call_time) between 12 and 13
                 and b.call_time    is not null then 1 end)             as calls_1214
    ,count(case when extract(hour from b.call_time) between 12 and 13
                 and b.contact_time is not null then 1 end)             as contacts_1214
    ,count(distinct case when extract(hour from b.call_time) between 12 and 13
                          and b.contact_duration >= 5
                          then b.cust_phone end)                        as unique_contacts_1214
    ,count(case when extract(hour from b.call_time) between 12 and 13
                 and b.contact_duration >= 30 then 1 end)               as contacts_30s_1214
    ,sum(case when extract(hour from b.call_time) between 12 and 13
               and b.contact_duration >= 30
               then b.contact_duration end)                             as contact_duration_30s_1214

    -- ── Slot 14:00–16:00 ─────────────────────────────────────────────────
    ,count(case when extract(hour from b.call_time) between 14 and 15
                 and b.call_time    is not null then 1 end)             as calls_1416
    ,count(case when extract(hour from b.call_time) between 14 and 15
                 and b.contact_time is not null then 1 end)             as contacts_1416
    ,count(distinct case when extract(hour from b.call_time) between 14 and 15
                          and b.contact_duration >= 5
                          then b.cust_phone end)                        as unique_contacts_1416
    ,count(case when extract(hour from b.call_time) between 14 and 15
                 and b.contact_duration >= 30 then 1 end)               as contacts_30s_1416
    ,sum(case when extract(hour from b.call_time) between 14 and 15
               and b.contact_duration >= 30
               then b.contact_duration end)                             as contact_duration_30s_1416

    -- ── Slot 16:00–18:00 ─────────────────────────────────────────────────
    ,count(case when extract(hour from b.call_time) between 16 and 17
                 and b.call_time    is not null then 1 end)             as calls_1618
    ,count(case when extract(hour from b.call_time) between 16 and 17
                 and b.contact_time is not null then 1 end)             as contacts_1618
    ,count(distinct case when extract(hour from b.call_time) between 16 and 17
                          and b.contact_duration >= 5
                          then b.cust_phone end)                        as unique_contacts_1618
    ,count(case when extract(hour from b.call_time) between 16 and 17
                 and b.contact_duration >= 30 then 1 end)               as contacts_30s_1618
    ,sum(case when extract(hour from b.call_time) between 16 and 17
               and b.contact_duration >= 30
               then b.contact_duration end)                             as contact_duration_30s_1618

from base b
inner join dominant_campaign d
    on  b.call_date  = d.call_date
    and b.agent_call = d.agent_call
    and d.rn = 1

where b.call_date is not null
group by 1, 2, 3, 4, 5
order by 1 desc, 2, 3, 4
;
