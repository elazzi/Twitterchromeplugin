chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'archive') {
    const tweets = [];
    document.querySelectorAll('article').forEach((tweetElement) => {
      const media = [];
      tweetElement.querySelectorAll('img').forEach((img) => {
        media.push(img.src);
      });
      tweetElement.querySelectorAll('video').forEach((video) => {
        media.push(video.src);
      });
      const tweet = {
        text: tweetElement.innerText,
        media: media,
      };
      tweets.push(tweet);
    });
    chrome.runtime.sendMessage({ action: 'archiveData', data: tweets });
  }
});
