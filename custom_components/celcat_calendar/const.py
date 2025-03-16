"""Constants for the Celcat Calendar integration."""

DOMAIN = "celcat_calendar"

CONF_SHOW_HOLIDAYS = "show_holidays"
CONF_GROUP_BY = "group_by"
CONF_FILTERS = "filters"

GROUP_BY_OFF = "off"
GROUP_BY_CATEGORY = "category"
GROUP_BY_CATEGORY_COURSE = "category_course"
GROUP_BY_COURSE = "course"

REMEMBERED_STRIPS = "remembered_strips"

DEFAULT_NAME = "Celcat Calendar"
DEFAULT_SCAN_INTERVAL = 12
DEFAULT_SHOW_HOLIDAYS = False
DEFAULT_GROUP_BY = GROUP_BY_OFF
DEFAULT_FILTERS = {
    "course_title",
    "course_strip_modules",
    "course_strip_category",
    "professors_title",
    "rooms_title",
    "sites_title",
    "sites_remove_duplicates",
}
