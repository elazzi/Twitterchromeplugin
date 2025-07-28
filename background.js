importScripts('jszip.js');

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'archiveData') {
    const zip = new JSZip();
    const mediaFolder = zip.folder('media');
    let html = '<html><head><title>Twitter Bookmarks</title></head><body>';
    const promises = [];

    for (const tweet of request.data) {
      html += `<div><p>${tweet.text}</p>`;
      for (const mediaUrl of tweet.media) {
        const filename = mediaUrl.split('/').pop();
        html += `<img src="media/${filename}">`;
        promises.push(
          fetch(mediaUrl)
            .then((response) => response.blob())
            .then((blob) => {
              mediaFolder.file(filename, blob);
            })
        );
      }
      html += `</div><hr>`;
    }

    Promise.all(promises).then(() => {
      html += '</body></html>';
      zip.file('index.html', html);
      zip.generateAsync({ type: 'blob' }).then((content) => {
        chrome.downloads.download({
          url: URL.createObjectURL(content),
          filename: 'twitter_bookmarks.zip',
        });
      });
    });
  }
});
