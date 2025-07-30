chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'downloadTweet') {
    const tweetElement = document.querySelector('article');
    if (tweetElement) {
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
      chrome.runtime.sendMessage({ action: 'tweetData', data: tweet });
    }
  }
});
