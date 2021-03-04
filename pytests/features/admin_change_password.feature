Feature: Admin Change Password

  As an IBA admin
  So that I can change my password
  I want to goto change password page and update password

  Scenario: Change password with correct old password and correct new password
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
  
  Scenario: Change password with correct old password and wrong new password
    Given I have logged in with username iba_admin and password iba_sep_1
    When I goto change password page 
    And I fill out old password iba_sep_1 and matching new password iba and submit
    Then I should see the message saying Could not Update Password
    And I should change password iba_sep_2 back to old password iba_sep_1 and the page shows Could not Update Password