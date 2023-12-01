import omni.ui as ui


class NameValueItem(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text, value):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        self.value_model = ui.SimpleStringModel(value)
        self.children = None

    def __repr__(self):
        return f'"{self.name_model.as_string} {self.value_model.as_string}"'


class DictValueItem(ui.AbstractItem):
    """Dict item of the model"""

    def __init__(self, key):
        super().__init__()
        self.name_model = ui.SimpleStringModel(key)
        self.value_model = ui.SimpleStringModel("")
        self.key = key
        self.children = []

    def __repr__(self):
        return f'"{self.name_model.as_string}"'


class CustomDataAttributesModel(ui.AbstractItemModel):
    """
    Represents the model for name-value table of a prims customdata attributes
    """

    def __init__(self):
        super().__init__()
        self._usd_prim = None
        self._children = []

    def set_prim(self, usd_prim):
        # we reset the model with the new custom data
        self._usd_prim = usd_prim
        self._children = []
        for key in usd_prim.GetCustomData():
            custom_data_bykey = usd_prim.GetCustomDataByKey(key)
            print(type(custom_data_bykey))
            if type(custom_data_bykey) is dict:
                self._children.append(DictValueItem(key))
            else:
                self._children.append(NameValueItem(key, custom_data_bykey))
        self._item_changed(None)  # emit data changed

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if type(item) is DictValueItem:
            custom_data = self._usd_prim.GetCustomDataByKey(item.key)
            for key in custom_data:
                custom_data_bykey = self._usd_prim.GetCustomDataByKey(key)
                if type(custom_data_bykey) is dict:
                    item.children.append(DictValueItem(key, custom_data_bykey))
                else:
                    item.children.append(NameValueItem(key, str(custom_data[key])))
            return item.children
        elif item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._children

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 2

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel for the first column
        and second column.
        """
        return item.value_model if column_id == 1 else item.name_model
