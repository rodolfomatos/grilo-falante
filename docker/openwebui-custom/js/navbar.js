(function() {
    window.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('grilo-navbar')) return;

        var nav = document.createElement('div');
        nav.id = 'grilo-navbar';
        nav.className = 'grilo-nav';
        nav.innerHTML = `
            <div class="grilo-nav-left">
                <a href="/" class="grilo-nav-logo">Grilo Falante</a>
                <div class="grilo-nav-links">
                    <a href="/" class="grilo-nav-link">Chat</a>
                    <a href="/hub" class="grilo-nav-link">Hub</a>
                    <a href="/visualizer" class="grilo-nav-link">Visualizer</a>
                    <a href="/visualizer/graph" class="grilo-nav-link">Knowledge Graph</a>
                </div>
            </div>
        `;

        document.body.insertBefore(nav, document.body.firstChild);
    });
})();