with
sector_count as (
    select jsonb_array_length(declared_data -> 'canteen' -> 'sectors') as nombre_secteurs, *
    from data_teledeclaration
),
td_by_sector as (
    -- max sector count at 8 for now https://ma-cantine-metabase.cleverapps.io/question/583
    select declared_data -> 'canteen' -> 'sectors' -> 7 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 7 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 7 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 8
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 6 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 6 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 6 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 7
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 5 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 5 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 5 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 6
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 4 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 4 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 4 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 5
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 3 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 3 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 3 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 4
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 2 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 2 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 2 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 3
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 1 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 1 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 1 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 2
    union all
    select declared_data -> 'canteen' -> 'sectors' -> 0 ->> 'id' as sector_id, declared_data -> 'canteen' -> 'sectors' -> 0 ->> 'name' as sector_name, declared_data -> 'canteen' -> 'sectors' -> 0 ->> 'category' as sector_category, * from sector_count
    where nombre_secteurs = 1

    /*
    the above was generated by putting the following in the browser console and editing the output:

    for (let i=8; i > 0; i--) {
      console.log(`select declared_data -> 'canteen' -> 'sectors' -> ${i-1} ->> 'id' as sector_id, * from sector_count
    where nombre_secteurs = ${i}`)
    }
    */
),
td_by_sector_traduit as (
    select
      case
          when sector_category = 'enterprise' then 'entreprise'
          when sector_category = 'education' then 'education'
          when sector_category = 'administration' then 'administration'
          when sector_category = 'leisure' then 'loisirs'
          when sector_category = 'autres' then 'autres'
          when sector_category = 'social' then 'social et médico-social'
          when sector_category = 'health' then 'santé'
      end as catégorie_secteur,
      *
    from td_by_sector
)

select * from td_by_sector_traduit
