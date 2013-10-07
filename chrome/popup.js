// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/**
 * Global variable containing the query we'd like to pass to Flickr. In this
 * case, kittens!
 *
 * @type {string}
 */
var QUERY = 'kittens';

var urlSetter = {
  setUrl: function() {
    var req = new XMLHttpRequest();
    what = document.getElementById("what");
    what.value = 'four'
    req.send(null);
  },

  /**
   * Handle the 'onload' event of our kitten XHR request, generated in
   * 'requestKittens', by generating 'img' elements, and stuffing them into
   * the document for display.
   *
   * @param {ProgressEvent} e The XHR ProgressEvent.
   * @private
   */
  showPhotos_: function (e) {
    var kittens = e.target.responseXML.querySelectorAll('photo');
    for (var i = 0; i < kittens.length; i++) {
      var img = document.createElement('img');
      img.src = this.constructKittenURL_(kittens[i]);
      img.setAttribute('alt', kittens[i].getAttribute('title'));
      document.body.appendChild(img);
    }
  },

  /**
   * Given a photo, construct a URL using the method outlined at
   * http://www.flickr.com/services/api/misc.urlKittenl
   *
   * @param {DOMElement} A kitten.
   * @return {string} The kitten's URL.
   * @private
   */
  constructKittenURL_: function (photo) {
    return "http://farm" + photo.getAttribute("farm") +
        ".static.flickr.com/" + photo.getAttribute("server") +
        "/" + photo.getAttribute("id") +
        "_" + photo.getAttribute("secret") +
        "_s.jpg";
  }
};
chrome.tabs.getSelected(windowId, function(tab) {
    alert("current:"+tab.url);
});
var descfield = document.getElementById("why");
// add listener to descfield field
if(descfield){
    if(descfield.addEventListener){
        descfield.addEventListener("focus", function() {
            if (descfield.value == 'Why?'){
                descfield.value = '';
            }
        });
    };
};
var urlfield = document.getElementById("what");
// add listener to urlfield field
if(urlfield){
    if(urlfield.addEventListener){
        urlfield.addEventListener("click", function() {
            if (urlfield.value == 'http://'){
                urlfield.value = '';
            }
        });
    };
};
// Run our kitten generation script as soon as the document's DOM is ready.
document.addEventListener('DOMContentLoaded', function () {
  urlSetter.setUrl();
});
