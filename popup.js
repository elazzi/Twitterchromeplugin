document.getElementById('downloadButton').addEventListener('click', () => {
  const tweetUrl = document.getElementById('tweetUrl').value;
  if (tweetUrl) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'downloadTweet', url: tweetUrl });
    });
  }
});
