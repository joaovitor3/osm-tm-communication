ABOUT_OSM = (
    "[http://openstreetmap.org OpenStreetMap] offers an online map (and spatial database) "
    "which is updated by the minute. Various tools and services allow data extracts for GIS "
    "specialists, Routable Garmin GPS data, Smartphone GPS navigation, and other "
    "device-compatible downloads. With an internet connection, regular syncing "
    "is possible with open access to the community contributed data as it comes in, "
    "with OpenStreetMap's bulk data downloads ideal for use offline."
    "In addition, maps can also be printed to paper.\n"
    "[https://www.openstreetmap.org/#map=14/-13.5242/-71.9847&layers=H Browse the Activation "
    "Area (Peru in this example)] to get a feel for the data that is currently available. "
    "Different map styles including an Humanitarian style can be selected on the right side, "
    "and  some data may not render (appear) on the map, but could be exported "
    "from the underlying database (See export section below).\n"
)
EXPORT_OSM_DATA = (
    "See [[Downloading data]] for instructions on getting large scale map data, or see the focused exports below:"
    "*A custom export can be created using the [https://export.hotosm.org/v3/exports HOT Export Tool]"
    "*Regularly updated OpenStreetMap exports are available on the "
    "[https://data.humdata.org/search?organization=hot&ext_page_size=25&sort=score+desc%2C+metadata_modified+desc "
    "Humanitarian Data eXchange (HDX)]\n"
)
PAPER_MAPS = (
    "Poster size Maps and normal sized paper atlases of custom areas can be printed:\n"
    "*See [[OSM_on_Paper]] for an overview and list of platforms and services for printing maps.\n"
    "*We suggest [http://fieldpapers.org/ FieldPapers] '''Paper Maps''' with grid "
    "for field survey or general navigation purposes.\n"
)
OFFLINE_NAVIGATION = (
    "With the availibility of Small communication devices, ''Navigation Offline data proves to be very "
    "useful to the humanitarians deployed in foreign countries''. We support the humanitarian NGO's "
    "using navigation data and invite them to give us feedback on the utilization of these devices "
    "in the context of field deployment.\n"
    "*See [[Software/Mobile]] for more information on using OSM in portable devices.\n"
    "*See also [https://learnosm.org/en/mobile-mapping/ Mobile Mapping] on LearnOSM.org "
    "for information on mapping in the field.\n"
    "*[[MAPS.ME]] has become very popular for mobile navigation as it works well on most phones and offline.\n"
)
ABOUT_HOT = (
    "[[File:Hot logo with text.svg|235px|left]]\n"
    "* To learn more about the Humanitarian OpenStreetMap Team (HOT), explore more of our wiki-pages "
    "(root: [[HOT]]) or our website [http://hot.openstreetmap.org hotosm.org].  We are a global "
    "community of mostly volunteers, we are also a US Nonprofit able to contract with organizations "
    "(email info at hotosm.org to contact our staff), we are also a 501-c-3 "
    "[http://hot.openstreetmap.org/donate charitable organization].\n"
)
LEARN_TO_MAP = (
    "* Most of our volunteer needs are for remote OSM contributors, visit "
    "[http://learnosm.org LearnOSM.org] to get started.\n"
)
SECTION_HEADER_STYLE = '<div style="clear:both; background:beige;box-shadow:3px 3px 2px red;padding:0.4em;">'

PROJECT_PAGE_HEADER = (
    "{{languages}}<!--make the page name implicit so that links to versions of this page are not copied-->\n"
    "{| style=\"background: #EEEEEE; border: 1px #aaa solid; color: black;\" width=\"100%\" cellpadding=\"6\"\n|-"
    "|style=\"background-color: #E0EEE0; border-bottom:1px solid #aaaaaa; font-size: 130%;\" colspan=\"2\"| '''General Information'''\n"
)


PAGE_TEMPLATE = (
    f"{SECTION_HEADER_STYLE}\n"
    "= For Aid Organizations =\n"
    "== Map and Data Services ==\n"
    "</div>\n"
    "=== About OpenStreetMap ===\n"
    f"{ABOUT_OSM}"
    "=== Paper Maps ===\n"
    f"{PAPER_MAPS}"
    "=== Exporting OpenStreetMap data ===\n"
    f"{EXPORT_OSM_DATA}"
    "=== Offline Road Navigation with small devices ===\n"
    f"{OFFLINE_NAVIGATION}"
    f"{SECTION_HEADER_STYLE}\n"
    "== About this activation ==\n"
    "</div>\n"
    "=== About HOT ===\n"
    f"{OFFLINE_NAVIGATION}"
    "=== History of this activation ===\n"
    "=== Coordination ===\n"
    "=== Effor made ===\n"
    f"{SECTION_HEADER_STYLE}\n"
    "= For Mappers =\n"
    "== How you Can Contribute  ==\n"
    "</div>\n"
    "=== Learn to Map ===\n"
    f"{LEARN_TO_MAP}"
    "=== Mapping priority ===\n"
    f"{SECTION_HEADER_STYLE}\n"
    "== Available Imagery  ==\n"
    "</div>\n"
    "=== OSM Default Imagery Sources ===\n"
    "=== Alternative Imagery Sources ===\n"
    "==== How to add/use Alternative Imagery ====\n"
    f"{SECTION_HEADER_STYLE}\n"
    "== Potential Datasources  ==\n"
    "</div>\n"
    "=== Mapathon events ===\n"
)