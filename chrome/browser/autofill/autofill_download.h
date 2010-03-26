// Copyright (c) 2010 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_AUTOFILL_AUTOFILL_DOWNLOAD_H_
#define CHROME_BROWSER_AUTOFILL_AUTOFILL_DOWNLOAD_H_

#include <map>
#include <vector>
#include <string>

#include "base/scoped_ptr.h"
#include "base/scoped_vector.h"
#include "base/string16.h"
#include "chrome/browser/autofill/autofill_profile.h"
#include "chrome/browser/autofill/field_types.h"
#include "chrome/browser/autofill/form_structure.h"
#include "chrome/browser/net/url_fetcher.h"

// Handles getting and updating AutoFill heuristics.
class AutoFillDownloadManager : public URLFetcher::Delegate {
 public:
  enum AutoFillRequestType {
    REQUEST_QUERY,
    REQUEST_UPLOAD,
  };
  // An interface used to notify clients of AutoFillDownloadManager.
  class Observer {
   public:
    // Called when heuristic successfully received from server.
    // |form_signatures| - the signatures of the requesting forms.
    // |heuristic_xml| - server response.
    virtual void OnLoadedAutoFillHeuristics(
        const std::vector<std::string>& form_signatures,
        const std::string& heuristic_xml) = 0;
    // Called when heuristic either successfully considered for upload and
    // not send or uploaded.
    // |form_signature| - the signature of the requesting form.
    virtual void OnUploadedAutoFillHeuristics(
        const std::string& form_signature) = 0;
    // Called when there was an error during the request.
    // |form_signature| - the signature of the requesting form.
    // |request_type| - type of request that failed.
    // |http_error| - http error code.
    virtual void OnHeuristicsRequestError(const std::string& form_signature,
                                          AutoFillRequestType request_type,
                                          int http_error) = 0;
   protected:
    virtual ~Observer() {}
  };

  AutoFillDownloadManager();
  virtual ~AutoFillDownloadManager();

  // |observer| - observer to notify on successful completion or error.
  void SetObserver(AutoFillDownloadManager::Observer *observer);

  // Starts a query request to AutoFill servers. The observer is called with the
  // list of the fields of all requested forms.
  // |forms| - array of forms aggregated in this request.
  bool StartQueryRequest(const ScopedVector<FormStructure>& forms);

  // Start upload request if necessary. The probability of request going
  // over the wire are |positive_upload_rate_| if it was matched by
  // AutoFill, |negative_download_rate_| otherwise. Observer will be called
  // even if there was no actual trip over the wire.
  // |form| - form sent in this request.
  // |form_was_matched| - true if form was matched by the AutoFill.
  bool StartUploadRequest(const FormStructure& form, bool form_was_matched);

  // Cancels pending request.
  // |form_signature| - signature of the form being cancelled. Warning:
  // for query request if more than one form sent in the request, all other
  // forms will be cancelled as well.
  // |request_type| - type of the request.
  bool CancelRequest(const std::string& form_signature,
                     AutoFillRequestType request_type);

  void SetPositiveUploadRate(double rate) {
    DCHECK(rate >= 0.0 && rate <= 1.0);
    positive_upload_rate_ = rate;
  }

  void SetNegativeUploadRate(double rate) {
    DCHECK(rate >= 0.0 && rate <= 1.0);
    negative_upload_rate_ = rate;
  }

 private:
  struct FormRequestData {
    std::vector<std::string> form_signatures;
    AutoFillRequestType request_type;
  };

  // Initiates request to AutoFill servers to download/upload heuristics.
  // |form_xml| - form structure XML to upload/download.
  // |request_data| - form signature hash(es) and indicator if it was a query.
  // |request_data.query| - if true the data is queried and observer notified
  //   with new data, if available. If false heuristic data is uploaded to our
  //   servers.
  bool StartRequest(const std::string& form_xml,
                    const FormRequestData& request_data);

  // URLFetcher::Delegate implementation:
  virtual void OnURLFetchComplete(const URLFetcher* source,
                                  const GURL& url,
                                  const URLRequestStatus& status,
                                  int response_code,
                                  const ResponseCookies& cookies,
                                  const std::string& data);

  // For each requested form for both query and upload we create a separate
  // request and save its info. As url fetcher is identified by its address
  // we use a map between fetchers and info.
  std::map<URLFetcher*, FormRequestData> url_fetchers_;
  AutoFillDownloadManager::Observer *observer_;

  // Probability of the form upload. Between 0 (no upload) and 1 (upload all).
  // |positive_upload_rate_| is for matched forms,
  // |negative_upload_rate_| for non matched.
  double positive_upload_rate_;
  double negative_upload_rate_;

  // Needed for unit-test.
  int fetcher_id_for_unittest_;
};

#endif  // CHROME_BROWSER_AUTOFILL_AUTOFILL_DOWNLOAD_H_

