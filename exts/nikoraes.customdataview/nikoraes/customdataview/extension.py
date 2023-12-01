import omni.ext
import omni.ui as ui
from .customdata_viewmodel import CustomDataAttributesModel


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[nikoraes.customdataview] some_public_function was called with x: ", x)
    return x**x


class CustomdataViewExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._events = self._usd_context.get_stage_event_stream()
        self._stage_event_sub = self._events.create_subscription_to_pop(
            self._on_stage_event, name="customdataview"
        )
        self._customdata_model = CustomDataAttributesModel()
        self._selected_primpath_model = ui.SimpleStringModel("-")
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
