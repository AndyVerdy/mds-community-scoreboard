(function() {
  var BASE = 'https://andyverdy.github.io/mds-community-scoreboard/';
  var s = document.currentScript;
  var theme = s.getAttribute('data-theme') || 'light';
  var member = s.getAttribute('data-member') || '';

  var params = 'embed=1&_v=' + Date.now();
  if (theme) params += '&theme=' + encodeURIComponent(theme);
  if (member) params += '&member=' + encodeURIComponent(member);

  var f = document.createElement('iframe');
  f.src = BASE + '?' + params;
  f.style.cssText = 'width:100%;border:none;overflow:hidden;display:block;';
  f.setAttribute('scrolling', 'no');
  f.setAttribute('frameborder', '0');

  s.parentNode.insertBefore(f, s);

  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'mds-scorecard-resize') {
      f.style.height = e.data.height + 'px';
    }
  });
})();
