// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_UI_WEBUI_OPTIONS2_HOME_PAGE_OVERLAY_HANDLER2_H_
#define CHROME_BROWSER_UI_WEBUI_OPTIONS2_HOME_PAGE_OVERLAY_HANDLER2_H_
#pragma once

#include "base/values.h"
#include "chrome/browser/autocomplete/autocomplete.h"
#include "chrome/browser/autocomplete/autocomplete_controller_delegate.h"
#include "chrome/browser/ui/webui/options2/options_ui2.h"

namespace options2 {

class HomePageOverlayHandler
    : public OptionsPageUIHandler,
      public AutocompleteControllerDelegate {
 public:
  HomePageOverlayHandler();
  virtual ~HomePageOverlayHandler();

  // OptionsPageUIHandler implementation
  virtual void RegisterMessages() OVERRIDE;

  virtual void GetLocalizedValues(base::DictionaryValue*) OVERRIDE;

  virtual void Initialize() OVERRIDE;

  // AutocompleteControllerDelegate implementation.
  virtual void OnResultChanged(bool default_match_changed) OVERRIDE;

 private:
  void RequestAutocompleteSuggestions(const ListValue* args);

  scoped_ptr<AutocompleteController> autocomplete_controller_;

  DISALLOW_COPY_AND_ASSIGN(HomePageOverlayHandler);
};

}  // namespace options2

#endif  // CHROME_BROWSER_UI_WEBUI_OPTIONS2_HOME_PAGE_OVERLAY_HANDLER2_H_
