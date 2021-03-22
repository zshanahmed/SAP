# Created by nale at 3/21/21
Feature: Forgot Password
  Reset password with registered email address if users forget old passwords

  Scenario: I click on the Forgot Password button
    Given I am on login page
    When I click the button with id: "password-forgot"
    Then I should be on page with url: "http://127.0.0.1:8000/password-forgot/"

  Scenario: I fill out the form and submit it
    Given I have navigated to Forgot Password page
    When I fill in "haw@uiowa.edu" into element: "exampleInputEmail"
    And I click the button with id: "reset-password"
    Then I should be on page with url: "http://127.0.0.1:8000/password-forgot-done/"

  Scenario: Change password with correct new password and correct new password
    Given I have logged in with username iba_admin and password iba_sep_1
    When I goto change password page
    And I fill out old password iba_sep_1 and matching new password iba_sep_2 and submit
    Then I should see the message saying Password Updated Successfully
    And I should change password iba_sep_2 back to old password iba_sep_1 and the page shows Password Updated Successfully

  Scenario: Change password with wrong old password and correct new password
    Given I have logged in with username iba_admin and password iba_sep_1
    When I goto change password page
    And I fill out old password something_random and matching new password iba_sep_2 and submit
    Then I should see the message saying Could not Update Password
    And I should change password iba_sep_2 back to old password iba_sep_1 and the page shows Could not Update Password
