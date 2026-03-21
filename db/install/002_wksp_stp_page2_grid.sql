declare
    l_exists number;
begin
    select count(*)
      into l_exists
      from all_tables
     where owner = 'WKSP_STP'
       and table_name = 'STP_PAGE2_GRID';

    if l_exists = 0 then
        execute immediate q'[
            create table WKSP_STP.STP_PAGE2_GRID (
                ID   number not null,
                NAME varchar2(100 char),
                constraint STP_PAGE2_GRID_PK primary key (ID)
            )
        ]';
    end if;
end;
/

merge into WKSP_STP.STP_PAGE2_GRID t
using (
    select 1 as id, 'Fila 1' as name from dual
    union all
    select 2 as id, 'Fila 2' as name from dual
) s
on (t.id = s.id)
when matched then
    update set t.name = s.name
when not matched then
    insert (id, name)
    values (s.id, s.name);

commit;
