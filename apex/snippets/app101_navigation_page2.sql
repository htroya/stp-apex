prompt --application/shared_components/navigation/lists/editable_grid_entry
declare
    l_list_id     number;
    l_entry_count number;
begin
    select list_id
      into l_list_id
      from apex_application_lists
     where application_id = 101
       and list_name = 'Navigation Menu';

    select count(*)
      into l_entry_count
      from apex_application_list_entries
     where application_id = 101
       and entry_text = 'Editable Grid';

    if l_entry_count = 0 then
        wwv_flow_imp.component_begin (
            p_version_yyyy_mm_dd => '2024.11.30',
            p_release             => '24.2.14',
            p_default_workspace_id => 9007948669297661,
            p_default_application_id => 101,
            p_default_id_offset   => 0,
            p_default_owner       => 'WKSP_STP'
        );

        wwv_flow_imp_shared.create_list_item(
            p_id                         => wwv_flow_imp.id(10102000000000013),
            p_list_item_display_sequence => 20,
            p_list_item_link_text        => 'Editable Grid',
            p_list_item_link_target      => 'f?p=' || chr(38) || 'APP_ID.:2:' || chr(38) || 'APP_SESSION.::' || chr(38) || 'DEBUG.:::',
            p_list_item_icon             => 'fa-table',
            p_list_item_current_type     => 'TARGET_PAGE',
            p_list_id                    => l_list_id
        );

        wwv_flow_imp.component_end;
    end if;
end;
/
