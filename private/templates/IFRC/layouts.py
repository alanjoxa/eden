# -*- coding: utf-8 -*-

from gluon import *
from gluon.storage import Storage
from s3 import *

# =============================================================================
class S3MainMenuLayout(S3NavigationItem):
    """
        Application Main Menu Layout
    """

    @staticmethod
    def layout(item):
        """ Custom Layout Method """

        # Manage flags: hide any disabled/unauthorized items
        if not item.authorized:
            item.enabled = False
            item.visible = False
        elif item.enabled is None or item.enabled:
            item.enabled = True
            item.visible = True

        if item.enabled and item.visible:
            if item.parent is None:
                # The main menu
                items = item.render_components()
                return UL(items, _id="nav")
            else:
                if item.components:
                    # A submenu
                    items = item.render_components()
                    _class = item.selected and "highlight" or ""
                    return LI(A(item.label,
                                _href=item.url(),
                                _id=item.attr._id,
                                _class=_class),
                              UL(items, _class="sub-menu"))
                else:
                    # A menu item
                    return LI(A(item.label,
                                _href=item.url(),
                                _id=item.attr._id))
        else:
            return None

# =============================================================================
class S3OptionsMenuLayout(S3NavigationItem):
    """
        Controller Options Menu Layout
    """

    @staticmethod
    def layout(item):
        """ Custom Layout Method """

        # Manage flags: hide any disabled/unauthorized items
        if not item.authorized:
            enabled = False
            visible = False
        elif item.enabled is None or item.enabled:
            enabled = True
            visible = True

        if enabled and visible:
            if item.parent is not None:
                if item.enabled and item.authorized:
                    if item.components:
                        # Submenu
                        _class = ""
                        if item.parent.parent is None and item.selected:
                            _class = "highlight"
                        items = item.render_components()
                        if items:
                            items = LI(UL(items, _class="menu-extention"))

                        return [LI(A(item.label,
                                     _href=item.url(),
                                     _id=item.attr._id,
                                     _class=_class)), items]

                    else:
                        # Submenu item
                        if item.parent.parent is None:
                            _class = item.selected and "highlight" or ""
                        else:
                            _class = " "

                        return LI(A(item.label,
                                    _href=item.url(),
                                    _id=item.attr._id,
                                    _class=_class))
            else:
                # Main menu
                items = item.render_components()
                return UL(items, _id="main-sub-menu", _class="sub-menu")

        else:
            return None

# =============================================================================
class S3LanguageMenuLayout(S3NavigationItem):

    @staticmethod
    def layout(item):
        """ Language menu layout

            options for each entry:
                - lang_code: the language code
                - lang_name: the language name
            option for the menu
                - current_language: code of the current language
        """

        if item.enabled:
            if item.components:
                # The language menu itself
                current_language = current.T.accepted_language
                items = item.render_components()
                select = SELECT(items, value=current_language,
                                    _name="_language",
                                    _title="Language Selection",
                                    _onchange="S3.reloadWithQueryStringVars({'_language': $(this).val()});")
                form = FORM(select, _id="language_selector",
                                    _name="_language",
                                    _action="",
                                    _method="get")
                return form
            else:
                # A language entry
                return OPTION(item.opts.lang_name,
                              _value=item.opts.lang_code)
        else:
            return None

    # -------------------------------------------------------------------------
    def check_enabled(self):
        """ Check whether the language menu is enabled """

        if current.deployment_settings.get_L10n_display_toolbar():
            return True
        else:
            return False

# -----------------------------------------------------------------------------
# Shortcut
ML = S3LanguageMenuLayout

# =============================================================================
class S3PersonalMenuLayout(S3NavigationItem):

    @staticmethod
    def layout(item):

        if item.parent is None:
            # The menu
            items = item.render_components()
            if items:
                return DIV(UL(items), _class="pmenu-wrapper")
            else:
                return "" # menu is empty
        else:
            # A menu item
            if item.enabled and item.authorized:
                return LI(A(item.label, _href=item.url()))
            else:
                return None

# -----------------------------------------------------------------------------
# Shortcut
MP = S3PersonalMenuLayout

# =============================================================================
class S3DashBoardMenuLayout(S3NavigationItem):
    """ Layout for the bottom-menu (dashboard menu) """

    @staticmethod
    def layout(item):

        T = current.T

        if item.components:
            items = item.render_components()
        else:
            items = None

        if item.parent is None:
            #return items
        #elif item.parent.parent is None:
            if items:
                if item.attr._id is not None:
                    _id = item.attr._id
                else:
                    _id = "sub-dashboard"
                return UL(items, _id=_id)
            else:
                return ""
        else:
            if item.components:
                return LI(A(H2(item.label),
                          UL(items),
                          IMG(_src=URL(c="static", f="themes",
                                       args=["IFRC", "img", item.opts.image]),
                              _alt=T(item.opts.title)),
                          _href=item.url()))
            elif item.opts.text:
                return LI(A(H2(item.label),
                          P(T(item.opts.text)),
                          IMG(_src=URL(c="static", f="themes",
                                       args=["IFRC", "img", item.opts.image]),
                              _alt=item.opts.image),
                          _href=item.url()))
            else:
                return LI(A(item.label, _href=item.url()))

# -----------------------------------------------------------------------------
# Shortcut
DB = S3DashBoardMenuLayout

# =============================================================================
class S3OrgMenuLayout(S3NavigationItem):
    """ Layout for the organisation-specific menu """

    @staticmethod
    def layout(item):

        name = "IFRC"
        logo = None

        # Lookup Root Organisation name & Logo
        root_org = current.auth.root_org()
        if root_org:
            s3db = current.s3db
            table = s3db.org_organisation
            record = current.db(table.id == root_org).select(table.name,
                                                             table.acronym,
                                                             table.logo,
                                                             limitby = (0, 1),
                                                             cache = s3db.cache,
                                                             ).first()
            if record:
                if record.acronym:
                    name = _name = record.acronym
                else:
                    _name = record.name
                    names = _name.split(" ")
                    names_with_breaks = []
                    nappend = names_with_breaks.append
                    for name in names:
                        nappend(name)
                        nappend(BR())
                    # Remove last BR()
                    names_with_breaks.pop()
                    name = TAG[""](*names_with_breaks)

                if record.logo:
                    size = (60, None)
                    image = s3db.pr_image_represent(record.logo, size=size)
                    url_small = URL(c="default", f="download", args=image)
                    alt = "%s logo" % _name
                    logo = IMG(_src=url_small,
                               _alt=alt,
                               _width=60,
                               )

        if not logo:
            # Default to generic IFRC
            logo = IMG(_src="/%s/static/themes/IFRC/img/dummy_flag.png" %
                            current.request.application,
                       _alt=current.T("Red Cross/Red Crescent"),
                       _width=60,
                       )

        # Note: render using current.menu.org.render()[0] + current.menu.org.render()[1]
        return (name, logo)

# -----------------------------------------------------------------------------
# Shortcut
OM = S3OrgMenuLayout

# END =========================================================================
