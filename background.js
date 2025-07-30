importScripts('jszip.js');

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'tweetData') {
    const tweet = request.data;
    const zip = new JSZip();
    const mediaFolder = zip.folder('media');
    let html = `<html><head><title>Tweet</title></head><body>`;
    const promises = [];

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
    html += `</div>`;

    Promise.all(promises).then(() => {
      html += '</body></html>';
      zip.file('tweet.html', html);
      zip.generateAsync({ type: 'blob' }).then((content) => {
        chrome.downloads.download({
          url: URL.createObjectURL(content),
          filename: 'tweet.zip',
        });
      });
    });
  }
});
