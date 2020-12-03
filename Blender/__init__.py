# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


bl_info = {
    "name": "Blender External Paint Reloaded",
    "author": "PointAtStuff (Original) - Zadirion (2.7x port) - zNightlord (2.80 port) ", # A 2.80 port
    "description": "Texture paint in an external image editor for Blender, with automatic refreshing in both ",
    "blender": (2, 80, 0),
    "version": (0, 2, 0),
    "location": "Image Editor > Side bar",
    "warning": "",
    "category": "Paint",
    "orginal_url": "https://sites.google.com/site/pointatstuffweb/external-paint-autorefresh"
}


import os

import bpy

from .Paint_Operators import *
from .UI_Panel import *

# Register & Unregister

classes = (IMAGEUI_PT_Paint,
IMAGE_OT_blenderextpaint_autorefresh_off,
IMAGE_OT_blenderextpaint_autorefresh_status,
IMAGE_OT_blenderextpaint_autorefresh_modal,
IMAGE_OT_blenderextpaint_autorefresh_switch_mode,
IMAGE_OT_blenderextpaint_autorefresh_save,
)

register, unregister = bpy.utils.register_classes_factory(classes)
