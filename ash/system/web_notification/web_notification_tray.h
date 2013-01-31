// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef ASH_SYSTEM_WEB_NOTIFICATION_WEB_NOTIFICATION_TRAY_H_
#define ASH_SYSTEM_WEB_NOTIFICATION_WEB_NOTIFICATION_TRAY_H_

#include "ash/ash_export.h"
#include "ash/system/tray/tray_background_view.h"
#include "ash/system/user/login_status.h"
#include "base/gtest_prod_util.h"
#include "base/memory/scoped_ptr.h"
#include "ui/message_center/message_center_tray.h"
#include "ui/message_center/message_center_tray_delegate.h"
#include "ui/views/bubble/tray_bubble_view.h"
#include "ui/views/widget/widget_observer.h"

// Status area tray for showing browser and app notifications. This hosts
// a MessageCenter class which manages the notification list. This class
// contains the Ash specific tray implementation.
//
// Note: These are not related to system notifications (i.e NotificationView
// generated by SystemTrayItem). Visibility of one notification type or other
// is controlled by StatusAreaWidget.

namespace message_center {
class MessageBubbleBase;
class MessageCenter;
class MessageCenterBubble;
class MessagePopupBubble;
}

namespace ash {

namespace internal {
class StatusAreaWidget;
class WebNotificationBubbleWrapper;
}

class ASH_EXPORT WebNotificationTray
    : public internal::TrayBackgroundView,
      public views::TrayBubbleView::Delegate,
      public message_center::MessageCenterTrayDelegate,
      public views::ButtonListener,
      public views::WidgetObserver {
 public:
  explicit WebNotificationTray(
      internal::StatusAreaWidget* status_area_widget);
  virtual ~WebNotificationTray();

  // Set whether or not the popup notifications should be hidden.
  void SetHidePopupBubble(bool hide);

  // Updates tray visibility login status of the system changes.
  void UpdateAfterLoginStatusChange(user::LoginStatus login_status);

  // Returns true if it should block the auto hide behavior of the launcher.
  bool ShouldBlockLauncherAutoHide() const;

  // Returns true if the message center bubble is visible.
  bool IsMessageCenterBubbleVisible() const;

  // Returns true if the mouse is inside the notification bubble.
  bool IsMouseInNotificationBubble() const;

  // Overridden from TrayBackgroundView.
  virtual void SetShelfAlignment(ShelfAlignment alignment) OVERRIDE;
  virtual void AnchorUpdated() OVERRIDE;
  virtual string16 GetAccessibleNameForTray() OVERRIDE;
  virtual void HideBubbleWithView(
      const views::TrayBubbleView* bubble_view) OVERRIDE;
  virtual bool ClickedOutsideBubble() OVERRIDE;

  // Overridden from internal::ActionableView.
  virtual bool PerformAction(const ui::Event& event) OVERRIDE;

  // Overridden from views::TrayBubbleView::Delegate.
  virtual void BubbleViewDestroyed() OVERRIDE;
  virtual void OnMouseEnteredView() OVERRIDE;
  virtual void OnMouseExitedView() OVERRIDE;
  virtual string16 GetAccessibleNameForBubble() OVERRIDE;
  virtual gfx::Rect GetAnchorRect(views::Widget* anchor_widget,
                                  AnchorType anchor_type,
                                  AnchorAlignment anchor_alignment) OVERRIDE;
  virtual void HideBubble(const views::TrayBubbleView* bubble_view) OVERRIDE;

  // Overridden from ButtonListener.
  virtual void ButtonPressed(views::Button* sender,
                             const ui::Event& event) OVERRIDE;

  // Overridden from WidgetObserver.
  virtual void OnWidgetClosing(views::Widget* widget) OVERRIDE;

  // Overridden from MessageCenterTrayDelegate.
  virtual void OnMessageCenterTrayChanged() OVERRIDE;
  virtual bool ShowMessageCenter() OVERRIDE;
  virtual void UpdateMessageCenter() OVERRIDE;
  virtual void HideMessageCenter() OVERRIDE;
  virtual bool ShowPopups() OVERRIDE;
  virtual void UpdatePopups() OVERRIDE;
  virtual void HidePopups() OVERRIDE;

  message_center::MessageCenter* message_center();

 private:
  FRIEND_TEST_ALL_PREFIXES(WebNotificationTrayTest, WebNotifications);
  FRIEND_TEST_ALL_PREFIXES(WebNotificationTrayTest, WebNotificationPopupBubble);
  FRIEND_TEST_ALL_PREFIXES(WebNotificationTrayTest,
                           ManyMessageCenterNotifications);
  FRIEND_TEST_ALL_PREFIXES(WebNotificationTrayTest, ManyPopupNotifications);

  // Queries login status and the status area widget to determine visibility of
  // the message center.
  bool ShouldShowMessageCenter();

 // Returns true if it should show the quiet mode bubble.
  bool ShouldShowQuietModeBubble(const ui::Event& event);

  // Shows the quiet mode bubble.
  void ShowQuietModeBubble();


  internal::WebNotificationBubbleWrapper* message_center_bubble() const {
    return message_center_bubble_.get();
  }

  internal::WebNotificationBubbleWrapper* popup_bubble() const {
    return popup_bubble_.get();
  }

  message_center::QuietModeBubble* quiet_mode_bubble() const {
    return quiet_mode_bubble_.get();
  }

  // Testing accessors.
  bool IsPopupVisible() const;
  message_center::MessageCenterBubble* GetMessageCenterBubbleForTest();
  message_center::MessagePopupBubble* GetPopupBubbleForTest();

  scoped_ptr<message_center::MessageCenterTray> message_center_tray_;
  scoped_ptr<internal::WebNotificationBubbleWrapper> message_center_bubble_;
  scoped_ptr<internal::WebNotificationBubbleWrapper> popup_bubble_;
  scoped_ptr<message_center::QuietModeBubble> quiet_mode_bubble_;
  views::ImageButton* button_;

  bool show_message_center_on_unlock_;

  DISALLOW_COPY_AND_ASSIGN(WebNotificationTray);
};

}  // namespace ash

#endif  // ASH_SYSTEM_WEB_NOTIFICATION_WEB_NOTIFICATION_TRAY_H_
