delete
  from WKSP_STP.STP_PAGE2_GRID
 where id not in (1, 2);

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
