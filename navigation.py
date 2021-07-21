"""
This module contains the Navigation methods,
the page object for the GC navigation menu.
"""
import datetime
import os
import pandas as pd
import fnmatch
from pyexcel.cookbook import merge_all_to_a_book
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from lib.ui.BasePage import BasePage
from datetime import datetime
from datetime import date
import os
import time


class Endpoints(object):

    LOGOUT = (By.XPATH, "//button[contains(text(),'Logout')]")
    COLLAPSE_BUTTON = (By.CLASS_NAME, 'collapse-btn')
    LINK = (By.XPATH, "//a[text() = '{}']")
    SIDE_MENU = (By.CLASS_NAME, 'site-nav__nav-container')
    SIDE_MENU_ITEM = (By.XPATH, "//span[contains(text(),'{}')]")
    GRID = (By.XPATH, ".//div[@role='grid']")
    GRID_HEADERS = (By.XPATH, "//div[@class='ag-header-cell ag-header-cell-sortable']")
    GRID_HEADER_TEXT = (By.XPATH, ".//span[@role='columnheader']")
    GRID_HEADER_SORT = (By.CLASS_NAME, "ag-header-cell-sortable")             # used to sort by col header asc/desc
    GRID_HEADER_MENU_BUTTON = (By.XPATH, "//span[@ref='eMenu']")
    GRID_FILTER_MENU = (By.XPATH, "//div[@class='ag-menu ag-ltr']")
    GRID_FILTER_MENU_TAB = (By.XPATH, "//div[@ref='tabHeader']")
    GRID_ROW_CONTAINER = (By.CLASS_NAME, 'ag-center-cols-container')
    ALL_GRID_ROWS = (By.XPATH, ".//div[@role='row']")
    GRID_ROW = (By.XPATH, "//div[@ref='eCenterContainer']/div[@row-id='{}']")
    SUBMENU_CONTAINER = (By.XPATH, "//div[@class='action-menu--container']")
    BURGER_MENU = (By.XPATH, ".//span[@class='ag-icon ag-icon-menu']")
    FILTER_MENU = (By.XPATH, ".//span[@class='ag-icon ag-icon-filter']")
    #FILTER_TEXT = (By.ID, 'filterText')
    FILTER_TEXT = (By.XPATH, "//input[@placeholder='Filter...']")
    FILTER_DROP_DOWN = (By.ID, 'filterType')
    HORIZONTAL_SCROLL = (By.XPATH, "//div[@ref='eBodyHorizontalScrollViewport']")
    MODAL_CLOSE_X = (By.CLASS_NAME, "btn-close")
    LOADING_CONTENT = (By.XPATH, "div[@class='loading-indicator__content']")
    LOADING_MESSAGE = (By.XPATH, "//span[@class='loading-indicator__message']")
    MODAAL_HEADER = (By.XPATH, "//div[@class='modaal-content-container']//h3")
    MODAAL_BUTTON = (By.XPATH,"//button[contains(@class,'modaal-confirm-btn')]/span[contains(text(),'{}')]")
    DRAWER_HEADER = (By.XPATH, "//p[@data-automation-id='drawer-heading-{}']")
    DRAWER_CLOSE = (By.XPATH, "//button[@data-automation-id='button-close-drawer']")

    LOADING_GIF = (By.XPATH, "//div[@class='loading-indicator']")
    FREQ_SELECT = (By.XPATH, "//div[@class='u-float-left calendar-type']//select")
    FREQ_OPTIONS = (By.XPATH, "//option[contains(text(),'{}')]")
    GRID_HEADER = (By.CLASS_NAME, "ag-header-cell-sortable")
    GRID_ACTION_COL = (By.CLASS_NAME, 'ag-pinned-right-cols-container')
    AUTOSIZE_COL = (By.XPATH, "//span[contains(text(),'{}')]")
    PIN_MENU = (By.XPATH, "//span[contains(text(),'Pin Column')]")
    PIN_OPTION = (By.XPATH, "//span[contains(text(),'{}')]")
    ACTION_SUBMENU = (By.XPATH, "//div[contains(text(),'{}')]")

class NavigationPage(BasePage):

    # Initializer
    def __init__(self, driver):
        BasePage.__init__(self, driver)

    #def login(self):
    #    base_url = os.getenv('GC_BASE_URL_UI', 'https://qagc.vertexsmb.com/')
    #    self.driver.get(base_url)

    def login(self):
        username = os.getenv('GC_ADMIN_USERNAME','VertexUser7646')
        password = os.getenv('GC_PASSWORD','B0necru$h3r')
        base_url = os.getenv('GC_BASE_URL_UI', 'https://qagc.vertexsmb.com/')
        self.driver.get(base_url)

        try:
            self.driver.maximize_window()
            time.sleep(0.5)
        except WebDriverException:
            pass

        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='username']")))
        usernameTextBox = self.driver.find_element(By.XPATH, "//input[@name='username']")
        passwordTextBox = self.driver.find_element(By.XPATH, "//input[@name='password']")
        usernameTextBox.send_keys(username)
        passwordTextBox.send_keys(password)
        button = self.driver.find_element(By.XPATH, ".//button[contains(text(),'Login')]")
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(button).perform()
        actionChains.click(button).perform()

        #UI is default loading page; wait for 'loading' gif to disapear
        self._wait_for_loading_gif()

    def logout(self):
        """
        Clicks the logout icon in the top right of the application.

        :return: None
        """
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(Endpoints.LOGOUT))
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable(Endpoints.LOGOUT))
        actionChains = ActionChains(self.driver)
        theElem = self.driver.find_element(*Endpoints.LOGOUT)
        actionChains.move_to_element(theElem).perform()
        actionChains.click(theElem).perform()
        time.sleep(2)

    def refresh_browser(self):
        """
        Refreshes the current browser page.

        :return: None
        """

        self.driver.refresh()

    def browser_back(self):

        """Clicks the browser back button"""

        self.driver.back()

    def minimize_browser(self):

        """Minimizes browser window"""

        self.driver.minimize_window()

    def maximize_browser(self):

        """Maximizes browser window"""

        self.driver.maximize_window()

    def switch_driver_tab(self):

        """Switches the drivr focus to the next tab in browser"""

        handles = self.driver.window_handles
        size = len(handles)
        parent_handle = self.driver.current_window_handle
        for x in range(size):
            if handles[x] != parent_handle:
                self.driver.switch_to.window(handles[x])
                print('title is ',self.driver.title)
                break

    def verify_logout(self):
        """after logout it redirect to logout page."""
        get_current_url = self.driver.current_url
        print("current_url after logout:" + get_current_url)
        print(get_current_url.find('identity/logout'))
        if 'identity/logout' not in get_current_url:
            assert False, "Error: User is not redirect to logout page."

    ############################
    #   Side Menu Components   #
    ############################

    def collapse_menu(self):

        """
        Clicks the Collapse Menu arrow button in the bottom left navigation menu

        :return: None
        """
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(Endpoints.COLLAPSE_BUTTON))
        self.driver.find_element(*Endpoints.COLLAPSE_BUTTON).click()

    def menu_click(self, menuName):
        """
        Clicks the desired menu from the left side navigation menu.
        Works with both nested and single menu items

        :param menuName:  Full menu name as appears in UI (case sensitive)
        :return: None
        """
        for x in range (30):
            try:
                self._click_expandable_side_menu(menuName)
                break
            except NoSuchElementException:
                pass
            try:
                self._click_single_side_menu(menuName)
                break
            except NoSuchElementException:
                assert False, menuName + " not found on side nav menu."

    #########################
    #   Action Components   #
    #########################

    def run_more_actions(self, action):
        """
        Will click the 'More Actions' button and selection and run the given action

        : param action: More Actions submen item to run (Ex: Print)"""

        self._css_button_click("More Actions")

        actionChains = ActionChains(self.driver)
        actionMenu = self.driver.find_element(*Endpoints.SUBMENU_CONTAINER)
        actionChains.move_to_element(actionMenu).perform()
        submenu = actionMenu.find_element(By.XPATH, "//div[contains(text(), '{}')]".format(action))
        actionChains.move_to_element(submenu).perform()
        submenu.click()
    def navigation_select_frequency(self, frequency):

        """
        This component will select Day, Week or Month on the UI page based on the frequency provided.

        :param frequency: Frequency to select as seen in the UI (Ex: Day, Weekm month)
        """
        #Current form select is not to standards and will be updated once VAT-3500 is fixed
        #Wait for selection box then click to show options
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(Endpoints.FREQ_SELECT))
        actionChains = ActionChains(self.driver)
        select = self.driver.find_element(*Endpoints.FREQ_SELECT)
        actionChains.move_to_element(select).perform()
        actionChains.click(select).perform()
        time.sleep(3)
        freq = self.driver.find_element(By.XPATH, "//option[contains(text(),'{}')]".format(frequency))
        freq.click()
        select.click()

    def navigation_select_dateBox(self, selectedDate):
        """
        A component to access the date box for any date search automations
        on the UI screen. Takes no parameters, simply call it on a UI screen
        automated test and you can access the calendar. From there use the
        '_date_picker_calender_widget' in the tax data details class to sort through
        the calendar.
        """
        actionCol = self.driver.find_element(By.CSS_SELECTOR,
                                             "div.react-datepicker-wrapper")
        # actionMenu = actionCol.find_element(By.XPATH, "//input[@class= 'date-field react-datepicker-ignore-onclickoutside']")
        actionMenu = actionCol.find_element(By.TAG_NAME, "input")
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(actionCol).perform()
        actionMenu.click()
        time.sleep(5)
        self._date_picker_calender_widget(selectedDate)

    def _date_picker_calender_widget(self, date):

        """Internal component to select date (DD MMM YYYY) in calendar widget"""

        # Date to select as time tuple
        selectDate = time.strptime(date, "%d %b %Y")

        # Current date as time tuple
        currentDate = time.localtime()

        # Find dif in months between current month/year and desired month year
        yearDif = selectDate.tm_year - currentDate.tm_year
        monthDif = selectDate.tm_mon - currentDate.tm_mon
        totalClicks = yearDif * 12 + monthDif

        # Click previous or next months arrows
        if totalClicks == 0:
            pass
        elif totalClicks < 0:
            prevMonth = self.driver.find_element(By.XPATH,
                                                 ".//button[@class='react-datepicker__navigation react-datepicker__navigation--previous']")
            count = 0
            while count < abs(totalClicks):
                try:
                    prevMonth.click()
                except WebDriverException:
                    assert False, "Previous scroller in calender window is not clickable"

                time.sleep(2)
                count = count + 1
        elif totalClicks > 0:
            nextMonth = self.driver.find_element(By.XPATH,
                                                 "//button[@class='react-datepicker__navigation react-datepicker__navigation--next']")
            count = 0
            while count < abs(totalClicks):
                try:
                    nextMonth.click()
                except WebDriverException:
                    assert False, "Next scroller in calender window is not clickable"
                time.sleep(2)
                count = count + 1

        # select day
        dayContainer = self.driver.find_element(By.XPATH, ".//div[@role='listbox']")
        # day = dayContainer.find_element(By.XPATH, "//div[contains(text(), '{}')]".format(str(selectDate.tm_mday)))
        # day.click()
        rows = dayContainer.find_elements_by_class_name('react-datepicker__week')
        foundDay = []
        for row in rows:
            days = row.find_elements_by_xpath(".//div[@role='option']")
            for day in days:
                # finds any matching day number and place xpath into list
                if day.text == str(selectDate.tm_mday):
                    foundDay.append(day)

        # selects the last number in the list in case both numbers are showing up from previous month
        if len(foundDay) > 1 and selectDate.tm_mday > 10:
            self.driver.execute_script("arguments[0].click();", foundDay[-1])
        elif len(foundDay) == 0:
            assert False, "Unable to find day: {}".format(str(selectDate.tm_mday))
        else:
            self.driver.execute_script("arguments[0].click();", foundDay[0])

    ####################################
    #   Side Drawer Components   #
    ####################################

    def close_side_drawer_by_x(self):

        """Closes the side drawer by clicking the "x" in the upper right hand corner"""

        actionChains = ActionChains(self.driver)
        element = self.driver.find_element(*Endpoints.DRAWER_CLOSE)
        actionChains.move_to_element(element).perform()
        actionChains.click(element).perform()

        # element = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(Endpoints.DRAWER_CLOSE))
        # actionChains = ActionChains(self.driver)
        # actionChains.move_to_element(element).perform()
        # actionChains.click(element).perform()

    def close_side_drawer_click_grey_area(self):
        """
        Closes the floating side drawer by clicking in the grey area

        :return:  None
        """
        actionChains = ActionChains(self.driver)
        element = self.driver.find_element(By.CLASS_NAME, "app-name__container")
        actionChains.move_to_element(element).perform()
        actionChains.click(element).perform()

    def verify_drawer_header(self, expectedHeader):
        """
        Verifies the drawer header matches the expected value.

        :param expectedHeader: Expected string to appear in drawer header.
        :return: None
        """
        # Standard for drawer header data-automation-id is 'drawer-heading-{} where {} is header in camelCase'
        components = expectedHeader.split(' ')
        headerCamel = components[0].lower() + ''.join(x.title() for x in components[1:])
        xpath = self._format_tuple(Endpoints.DRAWER_HEADER, headerCamel)
        content = self.driver.find_element(*xpath).text
        assert expectedHeader == content, "Expected and Actual header do not match. Expected: {e} Actual: {a}".format(e=expectedHeader, a=content)

    ########################
    #   Click Components   #
    ########################

    def click_button(self, textOnButton):
        """
        Clicks a button with the specified text on the UI

        : param textOnButton : Text of button as it appears in the UI
        : return : None
        """
        try:
            self._css_button_click(textOnButton)
        except NoSuchElementException:
            assert False, textOnButton + " button not found."

    def click_link(self, linkText):
        """
        Clicks a link on the UI with the given text

        :param linkText: Text of link as it appears in the UI
        :return: Launches new tab in Chrome
        """

        xpath = self._format_tuple(Endpoints.LINK, linkText)
        print(xpath)
        #WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(xpath))
        actionChains = ActionChains(self.driver)
        elem = self.driver.find_element(*xpath)
        actionChains.move_to_element(elem).perform()
        actionChains.click(elem).perform()


    def verify_link(self, linkText):
        """this component find the link by link text and validate it with linkText parameter.
        :param linkText: type 'str', Text of link as it appears in the UI
        :return: None
        """
        try:
            link_element = self.driver.find_element_by_link_text(linkText)
            actual_link_text = link_element.text
            print("linkText:"+ link_element.text)
        except:
            print("Error: link doesn't exist.")
        assert actual_link_text == linkText, "Link could not find by Link Text."

    ###########################
    #   Verify Components    #
    ###########################

    def verify_page_header(self, expectedHeader):
        """
        Verifies the page header matches the expected page header

        :param expectedHeader: Expected string as appears in the UI
        :return: None
        """
        content = self.driver.find_element(By.ID, 'page-heading').text
        assert expectedHeader == content, "Expected and Actual header do not match. Expected: {e} Actual: {a}".format(e=expectedHeader, a=content)

    def verify_modaal_header(self, expectedHeader):
        """ Verifies the page header matches the expected page header.
        :param expectedHeader: Expected string as appears in the UI
        :return: None """
        try:
            header_ele = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(Endpoints.MODAAL_HEADER))
            header_ele.is_displayed()
            self.highlight_element(header_ele)
            print("SessionHeader:" + header_ele.text)
        except (NoSuchElementException, TimeoutException):
            print("Error: Modal Header could not find")
        assert header_ele.text == expectedHeader, 'Error: Modaal header not matching....'

    def verify_modaal_button(self, buttonTxt):
        """in frontend, validate Modaal button is present or not.
        :param buttonTxt: Expected string as appears in the UI
        :return: None"""
        self.buttonTxt = str(buttonTxt)
        try:
            button = self.driver.find_element_by_xpath("//button[contains(@class,'modaal-confirm-btn')]/span[contains(text(),'{}')]".format(self.buttonTxt))
            print("Button text:'{}'".format(button.text))
            self.highlight_element(button)
        except (NoSuchElementException, TimeoutException):
            print("Error: Modaal button could not find")
        assert button.text == self.buttonTxt.upper(), 'Button could not find'

    def click_modaal_button(self, buttonTxt):
        """in frontend, click perform in Modaal button.
        :param buttonTxt: Expected string as appears in the UI
        :return: None"""
        try:
            button = self.driver.find_element_by_xpath("//button[contains(@class,'modaal-confirm-btn')]/span[contains(text(),'{}')]".format(buttonTxt))
            print("Button text:'{}'".format(button.text))
            self.highlight_element(button)
            button.click()
        except (NoSuchElementException, TimeoutException):
            assert False, "Error: Modaal button could not find"

    def verify_field_text(self, expectedTxt):
        """ Validate the fields text on the UI screen.
        : return :False when pram text no found. when find the text return :True
        """
        self.expectedTxt = str(expectedTxt)
        try:
            return self.driver.find_element_by_xpath("//*[text()='{}']".format(self.expectedTxt)).is_displayed()
        except NoSuchElementException:
            return False

    def verify_loading_spinner(self, isVisible='true'):
        """
        Verifies if the spinning animation is current visible on the UI screen.

        : param isVisible : Expected if spinning animation is visible in the UI; Defaults to true
        : return : None
        """
        try:
            self.driver.find_element(*Endpoints.LOADING_MESSAGE)
            if isVisible == 'true':
                WebDriverWait(self.driver, 60).until_not(EC.presence_of_element_located(Endpoints.LOADING_CONTENT))
                pass
            else:
                assert False, "Spinning animation was expected to be not visible but it is"
        except NoSuchElementException:
            if isVisible == 'false':
                pass
            else:
                assert False, "Spinning animation was expected to be visible but it is not"

    def verify_button(self, expectedBtnText, isVisible='true'):
        """
        Verifies if the button is visible and if the text on the button matches with the expected button text

        : param expectedBtnText : Expected string on button as appears in the UI
        : param isVisible : Expected button to be visible or not; Defaults to true
        : return : None
        """
        try:
            self.driver.find_element(By.XPATH, "//button[@type='button']//span[text() = '{}']".format(expectedBtnText))
            if isVisible == 'true':
                pass
            else:
                assert False, "Button was expected not to be found but it is visible with the text: {}".format(expectedBtnText)
        except NoSuchElementException:
            if isVisible == 'false':
                pass
            else:
                assert False, "Button was expected to be found but it is not visible with the text: {}".format(expectedBtnText)

    def verify_button_tooltip(self, button, expectedTip):

        """Will verify the tooltip popup of the given button

        :param button:  Name of button to Locates
        param expectedTip:  Expected tooltip to verify (as appears in the UI)"""

        actionChains = ActionChains(self.driver)
        button = self.driver.find_element(By.XPATH, "//button[text() = '{}']".format(button.capitalize()))
        hover = actionChains.move_to_element(button)
        hover.perform()
        time.sleep(5)
        actualTip = button.get_attribute('title')

        assert expectedTip == actualTip, "Expected and actual tooltip do not match.  Expected: {e} Actual: {a}".format(e=expectedTip, a=actualTip)

    def verify_tooltip(self, BtnText, expectedTip):
        """Will verify the tooltip popup of the locator
        :param BtnText: type 'str', Name of button to Locates
        :param expectedTip: type 'str', Expected tooltip to verify (as appears in the UI)
        :author: VertexUserTouhidul"""
        actualTip = ''
        try:
            button = self.driver.find_element(By.XPATH, "//button[@title= '{}']".format(BtnText))
            action = ActionChains(self.driver).move_to_element(button)
            action.pause(5).perform()
            actualTip = button.get_attribute('title')
        except:
            print("Error: element could not find for tooltip")
        assert expectedTip == actualTip, "Expected: '{0}' and Actual: '{1}' tooltip does not match.".format(expectedTip, actualTip)

    def verify_url(self, url):

        """Verifies that the given text string is in the url"""

        get_current_url = self.driver.current_url
        #print("current_url after logout:" + get_current_url)
        #print(get_current_url.find('identity/logout'))
        if url not in get_current_url:
            assert False, "Actual url does not match expected url"

    def navigation_verify_calender_scope(self, scope):
        """Verifies the reports displayed belong to the specified scope and date range
               :param scope: it specifies the scope of date range (Day,Week,Month)
        """

        time.sleep(10)
        parentCol = self.driver.find_element(By.CSS_SELECTOR,
                                             "div.react-datepicker-wrapper")
        calender_value = parentCol.find_element(By.TAG_NAME, "input").get_attribute("value")
        filename = self._get_latest_file_name()
        excel_file = filename
        merge_all_to_a_book(glob.glob(excel_file), "C:\\test\\_data\\output.xlsx")

        ReportData = pd.read_excel("C:\\test\\_data\\output.xlsx")
        StatutoryDueDate = ReportData['Statutory Due Date'].drop_duplicates()



        if scope == "Week":
            dates = calender_value.split('-')
            format = '%d %b %Y'
            start_date = datetime.strptime(dates[0].strip(), format)
            last_date = datetime.strptime(dates[1].strip(), format)

            for DateElement in StatutoryDueDate:
                if start_date <= DateElement.to_pydatetime() <= last_date:
                    pass
                else:
                    assert False, ("reports with statutory due date {} is found which is out of the specified scope".format(DateElement))

        elif scope == "Day":
            format = '%d %b %Y'
            date = datetime.strptime(calender_value, format)
            for DateElement in StatutoryDueDate:
                if date == DateElement.to_pydatetime():
                    pass
                else:
                    assert False, ("reports with statutory due date {} is found which is out of the specified scope".format(DateElement))

        else:
            for DateElement in StatutoryDueDate:
                if calender_value == DateElement.strftime("%B %Y"):
                    pass
                else:
                    assert False, ("reports with statutory due date {} is found which is out of the specified scope".format(DateElement))


    def _get_latest_file_name(self):
        list_of_files = glob.glob('C:/test/_data/*.csv')
        # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)
        return latest_file


    ########################
    #   Grid Components    #
    ########################

    def click_column_header(self, columnName):
        """
        This will click the column header once if found. Will raise an error if no header found matching the one given.

        :param columnHeader: Case sensitive header name.
        :return: None
        """
        grid = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        headers = grid.find_elements(*Endpoints.GRID_HEADER_SORT)
        for header in headers:
            print(header.text)
            if columnName == header.text:
                actionChains = ActionChains(self.driver)
                actionChains.move_to_element(header).perform()
                actionChains.click(header).perform()
                break
        else:
            assert False, 'No header found with the name ' + columnName


    def filter_column(self, columnName, filterType, filterText):

        """Selects the grid filter menu for the given column and filter type and enters text provided

        :param columnName: Name of column as it appears in the UI
        :param filterType: Type of filter. If filter is not needed, type in ''
        :param filterText: Text to enter in filter text box"""

        self._click_hamburger_menu(columnName)
        self._click_filter_menu()
        time.sleep(6)
        if filterType != '':
            self._select_filter_option(filterType)

        filterTextBox = self.driver.find_element(By.XPATH,"//input[@placeholder='Filter...']")
        filterTextBox.click()
        filterTextBox.clear()
        filterTextBox.send_keys(filterText)

    def filter_column_date_filter_options(self, columnName, filterType, filterText, filterTexttwo):
        """Selects the grid filter menu for the given column and filter type and enters text provided

        :param columnName: Name of column as it appears in the UI
        :param filterType: Type of filter. If filter is not needed, type in ''
        :param filterText: Text to enter in filter text box"""

        self._click_hamburger_menu(columnName)
        self._click_filter_menu()
        time.sleep(6)
        # if filterType != '':
        #     self._select_filter_option(filterType)

        filterTextBox = self.driver.find_element(By.XPATH,"//input[@placeholder='Filter...']")
        dropdown = self.driver.find_element(By.XPATH,"//span[@class = 'ag-icon ag-icon-small-down']")
        dropdown.click()
        self._select_filter_options(filterType)
        datevalue = self.driver.find_element(By.XPATH, "(//input[@class = 'ag-input-field-input ag-text-field-input'])[1]")
        datevalue.click()
        datevalue.clear()
        filterTextBox.send_keys(filterText)
        if filterType == "In Range" :
              time.sleep(6)
              datevaluetwo = self.driver.find_element(By.XPATH, "(//input[@class = 'ag-input-field-input ag-text-field-input'])[2]")
              time.sleep(6)
              datevaluetwo.click()
              datevaluetwo.clear()
              datevaluetwo.send_keys(filterTexttwo)


    def select_action(self, firstColName, firstObjName, action, hover='false', secColName='', secObjName=''):
        """
        Finds the row within the grid of specified column name(s) and object name(s) within the cell. This can be used to
        search up to 2 column names and its object within the cell. Selects the specified action on the Action menu.

        : param firstColName : Name of first column used for comparision
        : param firstObjName : Text within the cell under the first column name to search
        : param action : Action type from action menu section (E.g. Download Report)
        : param hover : Defaults to 'false' if hovering is not needed in Action menu
        : param secColName : Name of the second column used for comparison. Optional; leave it as '' if not needed
        : param secObjName : Text within the cell under the second column name to search. Optional; leave it as '' if not needed
        : return : None
        """

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))

        rowContainer = self.driver.find_element(*Endpoints.GRID_ROW_CONTAINER)
        rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
        for num, row in enumerate(rows):
            firstName = row.find_element_by_xpath(".//div[@col-id='" + self._retrieve_col_id(firstColName) + "']").text
            if secColName:
                secName = row.find_element_by_xpath(".//div[@col-id='" + self._retrieve_col_id(secColName) + "']").text
                if firstObjName == firstName and secObjName == secName:
                    numRow = str(num)
                    break
            else:
                if firstObjName == firstName:
                    numRow = str(num)
                    break
        else:
            if secColName:
                assert False, "Cannot find column names {} and {} with matching values of {} and {}".format(firstColName, secColName, firstObjName, secObjName)
            else:
                assert False, "Cannot find column name {} with matching value of {}".format(firstColName, firstObjName)

        self._find_action_row(numRow, action, hover)
        # gridHeaders = self.driver.find_element(*self.GRID_HEADERS)
        # headerCell = gridHeaders.find_element_by_xpath(".//div[@col-id='" + self._retrieve_col_id(columnName) + "']")
        # headerCell.find_element(*self.GRID_HEADER_MENU).click()
        # filterMenu = self.driver.find_element(*self.GRID_FILTER_MENU)
        # filterOption = filterMenu.find_elements_by_class_name('form-item')[0]
        # select correct options from drop-down list
        # enters text within the field
        # click button to filter

    def scroll_right_of_grid(self, columnName):
        """
        Scrolls the grid horizonally from left to right until it finds the specified column name.

        : param columnName : Name of column to find as shown in UI
        : return : None
        """
        self._scroll_to_grid()

        actionChains = ActionChains(self.driver)
        # Force the bar to the left at beginning
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()
        actionChains.send_keys(Keys.LEFT).perform()

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        grid = self.driver.find_element(*Endpoints.GRID)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADERS))
        headers = grid.find_elements(*Endpoints.GRID_HEADERS)
        headerList = []
        for header in headers:
            WebDriverWait(header, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADER_TEXT))
            headerText = header.find_element(*Endpoints.GRID_HEADER_TEXT).text
            headerList.append(headerText.lower())

        print(headerList)
        if columnName.lower() in headerList:
            getCol = grid.find_element_by_xpath("//span[@role='columnheader' and contains(text(), '" + columnName + "')]")
            self.driver.execute_script('arguments[0].scrollIntoView();', getCol)
            return
        # Start scrolling right until header if found or headers do not change (end of scroll)
        newHeaders = []
        while newHeaders != headerList:
            print('OLD', headerList)
            print('NEW', newHeaders)
            headerList = newHeaders
            # Scroll right 15 times.
            print('Scrolling Right...')
            actionChains = ActionChains(self.driver)
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            actionChains.send_keys(Keys.RIGHT).perform()
            time.sleep(2)
            newHeaders = []
            headers = grid.find_elements(*Endpoints.GRID_HEADERS)
            # Get all headers
            for header in headers:
                WebDriverWait(header, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADER_TEXT))
                headerText = header.find_element(*Endpoints.GRID_HEADER_TEXT).text
                newHeaders.append(headerText.lower())
            print(newHeaders)
            if columnName.lower() in newHeaders:
                getCol = grid.find_element_by_xpath("//span[@role='columnheader' and contains(text(), '" + columnName + "')]")
                self.driver.execute_script('arguments[0].scrollIntoView();', getCol)
                return

        assert False, 'No column found with the name ' + columnName

    def _select_value_from_dropdown(self, dropdownLabel, optionValue):
        dropDownElement = self.driver.find_element_by_xpath("//label[text() = '{}']/following-sibling::div//select".format(dropdownLabel))
        time.sleep(5)
        select = Select(dropDownElement)
        time.sleep(5)
        select.select_by_visible_text(optionValue)

    def _upload_file(self, label, filePath):
        element = self.driver.find_element_by_xpath("//label[text() = '{}']/following-sibling::div/input[@type = 'file']".format(label))
        element.send_keys(filePath)

    def scroll_down_of_grid(self, rowNum):
        """
        Finds the specified row number and scrolls down the grid if needed. Clicks on the row when found.

        : param rowNum : Row number to find, starting at 0
        """
        self._scroll_to_grid()
        actionChains = ActionChains(self.driver)

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        grid = self.driver.find_element(*Endpoints.GRID)
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID_ROW_CONTAINER))
        rowContainer = grid.find_element(*Endpoints.GRID_ROW_CONTAINER)
        rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
        rowList = []
        for row in rows:
            rowValue = row.get_attribute("row-index")
            #print(rowValue)
            rowList.append(str(rowValue))

        #print(rowList)
        if rowNum in rowList:
            getRow = rowContainer.find_element_by_xpath(".//div[@row-id='" + rowNum + "']")
            self.driver.execute_script('arguments[0].scrollIntoView();', getRow)
            actionChains.move_to_element(getRow).perform()
            actionChains.click(getRow).perform()
            time.sleep(5)
            return
        # Scroll to the last row displayed on grid
        #print(rowList[-1])
        getRow = rowContainer.find_element_by_xpath(".//div[@row-id='" + rowList[-1] + "']")
        self.driver.execute_script('arguments[0].scrollIntoView();', getRow)

        # Start scrolling right until header if found or headers do not change (end of scroll)
        newRows = []
        while newRows != rowList:
            #print('OLD', rowList)
            #print('NEW', newRows)
            rowList = newRows
            # Scroll down 15 times.
            print('Scrolling Down...')
            for e in range(4):
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
            time.sleep(2)
            newRows = []
            rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
            # Get all headers
            for row in rows:
                rowValue = row.get_attribute("row-index")
                #print(rowValue)
                newRows.append(str(rowValue))
            #print(newRows)
            if rowNum in newRows:
                getRow = rowContainer.find_element_by_xpath(".//div[@row-id='" + rowNum + "']")
                self.driver.execute_script('arguments[0].scrollIntoView();', getRow)
                actionChains.move_to_element(getRow).perform()
                actionChains.click(getRow).perform()
                time.sleep(5)
                return

        assert False, 'No row found with the number {}'.format(rowNum)

    def edit_row_values_in_grid(self, cellValue, rowNum, columnName):
        """
        **IN PROGRESS - DO NOT USE**
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        grid = self.driver.find_element(*Endpoints.GRID)
        # finds the row index
        xpath = self._format_tuple(Endpoints.GRID_ROW, int(rowNum))
        row = grid.find_element(*xpath)
        # finds the column name
        rowCell = row.find_element(By.XPATH, ".//div[@col-id='" + columnName + "']")

        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.double_click(rowCell).perform()
        cellBox = rowCell.find_element(By.TAG_NAME, 'input')
        cellBox.send_keys(cellValue)
        cellBox.send_keys(Keys.ENTER)

    def verify_edit_values_in_grid(self, expectedEdit):
        """
        **IN PROGRESS - DO NOT USE**
        """
        grid = self.driver.find_element(*Endpoints.GRID)
        # grid.find_element_by_xpath()

    ########################
    #   Misc Components    #
    ########################

    def title(self):
        return self.driver.title

    def click_on_body(self):
        """
        Clicks on the body of the current page

        : param : None
        """
        self.driver.find_element_by_tag_name('body').click()


    def highlight_element(self, element):
        """ this will highlight the web element on the UI.
        :param: element: web element
        :author: VertexUserTouhidul"""
        #ele = self.driver.find_element(locator)
        self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "background:yellow; color: Red; border: 3px dotted solid yellow;")
        time.sleep(1)
        self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "backgroundColor: transparent; color: Green; border: 3px dotted solid yellow;")


    ############################
    #   Internal Components    #
    ############################

    def _find_action_row(self, numRow, action, hover):
        """ Finds the action row and clicks on the specified button """

        sideGrid = self.driver.find_element_by_class_name('ag-pinned-right-cols-container')
        row = sideGrid.find_element_by_xpath(".//div[@row-index='" + numRow + "']")
        if hover == 'true':
            actionChains = ActionChains(self.driver)
            actionChains.move_to_element(row).perform()
            button = row.find_element_by_xpath("//button[@type='button' and @title='" + action + "']")
            self.driver.execute_script("arguments[0].click();", button)
            #actionChains.click(button).perform()
        else:
            rowBox = row.find_element_by_xpath(".//div[@class='ag-react-container']")
            rowBox.find_element_by_xpath(".//button[@data-automation-id='button-commonGrid-actionMenuToggle']").click()
            actionMenu = self.driver.find_element_by_class_name('action-menu--container')
            actionMenu.find_element_by_xpath(".//div[@class='action-menu__item' and contains(text(), '" + action + "')]").click()

    def _scroll_to_grid(self):
        """ Scrolls the page down to the grid for visibility """

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.HORIZONTAL_SCROLL))
        scrollBar = self.driver.find_element(*Endpoints.HORIZONTAL_SCROLL)
        self.driver.execute_script("arguments[0].scrollIntoView()", scrollBar)

    def _retrieve_cell_from_grid(self, rowNum, columnName):
        """ internal component that retrieve specified cell based on row index and column name """

        # gets the correct grid from accordion
        grid = self.driver.find_element(*Endpoints.GRID)
        # finds the row index
        xpath = self._format_tuple(Endpoints.GRID_ROW, int(rowNum))
        row = grid.find_element(*xpath)
        # finds the column name
        rowCell = row.find_element(By.XPATH, ".//div[@col-id='" + columnName + "']")
        return rowCell

    def company_selection(self,value):
        Country_value=self.driver.find_element(By.XPATH,"//span[text() = 'Import']")
        Country_value.send_keys(value)
        Country_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        Country_container.click()

    def _verify_export_to_excel(self):
         try:
             self.driver.find_element(By.XPATH,"//div[text() = 'Export To Excel']")
             assert True
         except:
             assert False, "export to excel button is absent"

    def _export_to_excel(self):
        self.driver.find_element(By.XPATH,"//div[text() = 'Export To Excel']").click()

    def _validate_reporterui_headers(self, dataframe, columnheaders):
        actualcolumnheaders = dataframe.columns
        expectedcolumnheaders = columnheaders.split("|")
        print(expectedcolumnheaders)
        print(actualcolumnheaders)
        for i in range(0,len(actualcolumnheaders)):
            errormessage = actualcolumnheaders[i] + " not equal to " + expectedcolumnheaders[i]
            assert actualcolumnheaders[i] == expectedcolumnheaders[i]

    def _get_date_difference_in_days(self, futuredate, pastdate):
        date_format = '%Y-%m-%d'
        delta = datetime.strptime(futuredate, date_format) - datetime.strptime(pastdate, date_format)
        return delta.days

    def _validate_urgency_status(self, urgencycolumnvalues, duedatecolumnvalues):
        date_format = '%Y-%m-%d'
        today = date.today()
        for i in range(0,len(duedatecolumnvalues)):
            print(duedatecolumnvalues[i])
            days = self._get_date_difference_in_days(today.strftime(date_format), duedatecolumnvalues[i])
            print(days)
            if days > 0:
                assert urgencycolumnvalues[i] == 'Overdue'
            elif days <= 0 and days >= -2:
                assert urgencycolumnvalues[i] == 'Warning', "Stautary due date : " + duedatecolumnvalues[i] + "status : " + urgencycolumnvalues[i]
            else :
                assert urgencycolumnvalues[i] == 'On Track'

    def _validate_workflow_status(self, workflowstatuscolumnvalues):
        for i in range(0,len(workflowstatuscolumnvalues)):
            assert workflowstatuscolumnvalues[i] == 'Not Started', "workflow status is : " + workflowstatuscolumnvalues[i]

    def _validate_report_column_value(self, reportColumnvalue, expctedvalue):
        for i in range(0,len(reportColumnvalue)):
            assert reportColumnvalue[i] == expctedvalue, "column values are : " + reportColumnvalue[i]



    def _validate_report_column_value_date(self, reportColumnvalue,expectedvalue):
        for i in range(0,len(reportColumnvalue)):
            assert reportColumnvalue[i] == expectedvalue, "workflow status is : " + reportColumnvalue[i]


    def _validate_report_column_value_date_less(self, reportColumnvalue,expectedvalue):
        date_format = '%Y-%m-%d'
        for i in range(0,len(reportColumnvalue)):
            assert datetime.strptime(reportColumnvalue[i], date_format) < datetime.strptime(expectedvalue, date_format), "workflow status is : " + reportColumnvalue[i]

    def _validate_report_column_value_date_greater_than(self, reportColumnvalue,expectedvalue):
        date_format = '%Y-%m-%d'
        for i in range(0,len(reportColumnvalue)):
            assert datetime.strptime(reportColumnvalue[i], date_format) > datetime.strptime(expectedvalue, date_format), "workflow status is : " + reportColumnvalue[i]

    def _validate_report_column_value_not_equal(self, reportColumnvalue,expectedvalue):
        date_format = '%Y-%m-%d'
        for i in range(0,len(reportColumnvalue)):
            assert datetime.strptime(reportColumnvalue[i], date_format) != datetime.strptime(expectedvalue, date_format), "workflow status is : " + reportColumnvalue[i]

    def _validate_report_column_value_date_range(self, reportColumnvalues,dateOne, dateTwo):
        date_format = '%Y-%m-%d'
        for i in range(0,len(reportColumnvalues)):
            assert datetime.strptime(dateOne, date_format) < datetime.strptime(reportColumnvalues[i], date_format) < datetime.strptime(dateTwo, date_format), "workflow status is : " + reportColumnvalue[i]



    def _validate_date_column_sorted_or_not(self, statutarycolumnvalue):
        date_format = '%Y-%m-%d'
        date_list = []
        for i in range(0,len(statutarycolumnvalue)):
            date_list.append(datetime.strptime(statutarycolumnvalue[i], date_format))
        sorted_list = date_list[:]
        sorted_list.sort()
        assert sorted_list == date_list

    def filter_column_with_checkbox(self, columnName, filtervalue):

        """Selects the grid filter menu for the given column and filter type and enters text provided

        :param columnName: Name of column as it appears in the UI
        :param filterType: Type of filter. If filter is not needed, type in ''
        :param filterText: Text to enter in filter text box"""

        self._click_hamburger_menu(columnName)
        self._click_filter_menu()
        time.sleep(6)
        # if filterType != '':
        #     self._select_filter_option(filterType)

        filterTextBox = self.driver.find_element(By.XPATH,"//input[@placeholder='Filter...']")
        select_all = self.driver.find_element(By.XPATH, "//input[@name = '(Select all)']")
        select_all.click()
        Country_container = self.driver.find_element(By.XPATH, "//input[@name = '{}']".format(filtervalue))
        Country_container.click()

    def _validate_text_and_number_column_sorted_or_not(self, statutarycolumnvalue):
        list = []
        for i in range(0,len(statutarycolumnvalue)):
            list.append(statutarycolumnvalue[i])
        sorted_list = list[:]
        sorted_list.sort()
        assert sorted_list == list

    def validate_cell_editable_or_not(self, rowNum, columnName):
        """
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.double_click(rowCell).perform()
        try:
            cellBox = rowCell.find_element(By.TAG_NAME, 'input')
            cellBox.send_keys('Dont Enter')
        except:
            assert True
        else:
            assert False


    def _validate_urgency_status_colour(self, urgencyStatus):
         colour = self.driver.find_element(By.XPATH, "//div[@title = '{}']/*[local-name() = 'svg']/*[local-name() = 'path']".format(urgencyStatus))
         if urgencyStatus == 'On Track':
            assert colour.get_attribute("fill") == "#0064D6"


    def _select_filter_options(self, filteroption):
        if filteroption == 'Less Than':
           actionChains = ActionChains(self.driver)
           actionChains.send_keys(Keys.DOWN).perform()
           actionChains.send_keys(Keys.ENTER).perform()
        elif filteroption == 'Greater Than':
           actionChains = ActionChains(self.driver)
           actionChains.send_keys(Keys.DOWN).perform()
           actionChains.send_keys(Keys.UP).perform()
           time.sleep(2)
           actionChains.send_keys(Keys.ENTER).perform()
           time.sleep(2)
        elif filteroption == 'In Range':
            actionChains = ActionChains(self.driver)
            actionChains.send_keys(Keys.DOWN).perform()
            actionChains.send_keys(Keys.DOWN).perform()
            actionChains.send_keys(Keys.ENTER).perform()
            time.sleep(6)
        elif filteroption == 'Not Equal' :
            time.sleep(6)
            actionChains = ActionChains(self.driver)
            actionChains.send_keys(Keys.DOWN).perform()
            time.sleep(2)
            actionChains.send_keys(Keys.DOWN).perform()
            time.sleep(2)
            actionChains.send_keys(Keys.UP).perform()
            time.sleep(2)
            actionChains.send_keys(Keys.ENTER).perform()

        elif filteroption == 'Equals':
            actionChains = ActionChains(self.driver)
            actionChains.send_keys(Keys.ENTER).perform()
            time.sleep(2)















