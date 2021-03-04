Feature: Admin Change Password

  As an IBA admin
  So that I can change my password
  I want to goto change password page and update password

  Scenario: Change password with correct old password and matching new password
    Given I have logged in with username johndoe and password serpent_1
    When I goto change password page 
    And I fill out old password serpent_1 and matching new password serpent_2 and submit
    Then I should see the message saying Password Updated Successfully
    And I should change password serpent_2 back to old password serpent_1 and the page shows Password Updated Successfully
