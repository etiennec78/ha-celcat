"""Constants for the Celcat Calendar integration."""

DOMAIN = "celcat_calendar"

CONF_SHOW_HOLIDAYS = "show_holidays"
CONF_TITLE = "title"
CONF_DESCRIPTION = "description"
CONF_GROUP_BY = "group_by"
CONF_FILTERS = "filters"
CONF_REPLACEMENTS = "replacements"

ATTRIBUTE_ID = "id"
ATTRIBUTE_CATEGORY = "category"
ATTRIBUTE_COURSE = "course"
ATTRIBUTE_ROOMS = "rooms"
ATTRIBUTE_PROFESSORS = "professors"
ATTRIBUTE_MODULES = "modules"
ATTRIBUTES_DEPARTMENT = "department"
ATTRIBUTES_SITES = "sites"
ATTRIBUTES_FACULTY = "faculty"
ATTRIBUTES_NOTES = "notes"
ATTRIBUTES = [
    ATTRIBUTE_ID,
    ATTRIBUTE_CATEGORY,
    ATTRIBUTE_COURSE,
    ATTRIBUTE_ROOMS,
    ATTRIBUTE_PROFESSORS,
    ATTRIBUTE_MODULES,
    ATTRIBUTES_DEPARTMENT,
    ATTRIBUTES_SITES,
    ATTRIBUTES_FACULTY,
    ATTRIBUTES_NOTES,
]
ATTRIBUTES_SINGULAR = {
    ATTRIBUTE_ROOMS: "room",
    ATTRIBUTE_PROFESSORS: "professor",
    ATTRIBUTE_MODULES: "module",
    ATTRIBUTES_SITES: "site",
}

GROUP_BY_OFF = "off"
GROUP_BY_COURSE = "course"
GROUP_BY_CATEGORY = "category"
GROUP_BY_CATEGORY_COURSE = "category_course"

REMEMBERED_STRIPS = "remembered_strips"

DEFAULT_NAME = "Celcat Calendar"
DEFAULT_SCAN_INTERVAL = 12
DEFAULT_SHOW_HOLIDAYS = False
DEFAULT_TITLE = [
    ATTRIBUTE_CATEGORY,
    ATTRIBUTE_COURSE,
]
DEFAULT_DESCRIPTION = [
    ATTRIBUTE_ROOMS,
    ATTRIBUTE_PROFESSORS,
    ATTRIBUTES_SITES,
    ATTRIBUTES_FACULTY,
    ATTRIBUTES_NOTES,
]
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
DEFAULT_REPLACEMENTS = []
