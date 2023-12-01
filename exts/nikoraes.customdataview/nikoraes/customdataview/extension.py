import omni.ext
import omni.ui as ui
from functools import partial
from .customdata_viewmodel import CustomDataAttributesModel


class CustomDataViewExtension(omni.ext.IExt):
    WINDOW_NAME = "CustomData"
    MENU_PATH = f"Window/{WINDOW_NAME}"

    def on_startup(self, ext_id):
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._events = self._usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="customdataview"
        )
        self._customdata_model = CustomDataAttributesModel()
        self._selected_primpath_model = ui.SimpleStringModel("-")
        self._window = None
        ui.Workspace.set_show_window_fn(
            CustomDataViewExtension.WINDOW_NAME,
            partial(self.show_window, None),
        )

        # Add a Menu Item for the window
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                CustomDataViewExtension.MENU_PATH,
                self.show_window,
                toggle=True,
                value=True,
            )

        ui.Workspace.show_window(CustomDataViewExtension.WINDOW_NAME)

    def show_window(self, menu, value):
        # value is true if the window should be shown
        if value and not self._window:
            self._window = ui.Window("CustomData", width=300, height=200)

            with self._window.frame:
                with ui.VStack():
                    ui.Label("Selected Prim:", height=20)
                    self._selectedPrimName = ui.StringField(
                        model=self._selected_primpath_model, height=20, read_only=True
                    )

                    ui.Label("Custom Data:", height=20)
                    with ui.ScrollingFrame(
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                        style_type_name_override="TreeView",
                    ):
                        tree_view = ui.TreeView(
                            self._customdata_model,
                            root_visible=False,
                            header_visible=False,
                            columns_resizable=True,
                            column_widths=[ui.Fraction(0.5), ui.Fraction(0.5)],
                            style={"TreeView.Item": {"margin": 4}},
                        )
            # Handles the change in visibility of the window gracefully
            self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        elif self._window and value:
            self._window.visible = True
        elif self._window:
            self._window.visible = False

    def _on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._on_selection_changed()

    def _on_selection_changed(self):
        selection = self._selection.get_selected_prim_paths()
        stage = self._usd_context.get_stage()
        print(f"== selection changed with {len(selection)} items")
        if selection and stage:
            # -- set last selected element in property model
            if len(selection) > 0:
                path = selection[-1]
                self._selected_primpath_model.set_value(path)
                prim = stage.GetPrimAtPath(path)
                self._customdata_model.set_prim(prim)
            # -- print out all selected custom data
            for selected_path in selection:
                print(f" item {selected_path}:")
                prim = stage.GetPrimAtPath(selected_path)
                for key in prim.GetCustomData():
                    print(f"   - {key} = {prim.GetCustomDataByKey(key)}")

    def on_shutdown(self):
        # cleanup
        self._window = None
        self._stage_event_sub = None
