import re
import os
"""Page copy for the site. Setting and menu names match the app's own labels.

Values to bump at each release (the only place they live):
  REVIEWED_VERSION  the Library release the docs were last checked against
  REVIEWED_DATE     the "Last reviewed" date; None uses the build date
"""
import datetime

REVIEWED_VERSION = '1.6.1'
REVIEWED_DATE = None

# Set by build.py at build time: the latest releases from GitHub (or None when offline) and the Markdown converter.
RELEASES = None
to_html = None

LEFT = '<svg class="icon chevron" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m15 6-6 6 6 6"/></svg>'


def release_page(page, r):
    """One page per large release: summary, sidebar contents, sections, download line, Related."""
    toc = [(re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-'), h) for h, _ in r['sections']]
    toc.append(('download', 'Download'))
    sections = []
    for h, items in r['sections']:
        sid = re.sub(r'[^a-z0-9]+', '-', h.lower()).strip('-')
        sections.append((sid, h, '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'))
    tag = r['tag']
    download = (f'<p>Download Library {r["version"]} from the <a href="https://github.com/deansasek/library/releases/tag/{tag}" '
                'rel="noopener noreferrer">GitHub release page</a>, or install it with the command on the <a href="/install/">install page</a>.</p>')
    sections.append(('download', 'Download', download))
    return page('/whats-new/' + r['id'] + '/', f"What's new in Library {r['version']}", r['summary'], r['intro'], toc, sections,
                released=r['date'])


def render(page):
    out = {}

    # ---------- Guide ----------
    guide_toc = [
        ('get-started', 'Get started'), ('open-anything', 'Open anything'), ('find-it-with-quick-open', 'Find it with Quick Open'),
        ('keep-what-you-copy', 'Keep what you copy'), ('save-snippets', 'Save snippets'),
        ('organize-your-library', 'Organize your library'), ('edit-an-item', 'Edit an item'),
        ('add-notes', 'Add notes'), ('use-templates', 'Use templates'), ('read-later', 'Read later'),
        ('shortcuts', 'Shortcuts'), ('work-with-other-apps', 'Work with other apps'),
        ('stay-up-to-date', 'Stay up to date'), ('settings', 'Settings'),
        ('permissions', 'Permissions'), ('troubleshooting', 'Troubleshooting'),
    ]
    guide = [
        ('get-started', 'Get started', '<p>Install Library first, then follow the first steps in <a href="/install/#first-steps">Install</a>.</p>'),
        ('open-anything', 'Open anything', '''<p>Bookmarks, apps, folders, and terminal commands open from the menu bar, a keyboard shortcut, or Spotlight. To open an item the other way, hold Option while you click it.</p>
<ul>
<li><strong>Bookmarks</strong> open in a new tab or a new window.</li>
<li><strong>Apps</strong> come to the front. To start a new copy, add a launch argument, such as <code>--profile work</code>.</li>
<li><strong>Terminal commands</strong> run in a login shell in a new Terminal window. Add only commands you trust.</li>
<li><strong>Folders</strong> open all of their bookmarks and apps at once. Library asks first if there are more than five.</li>
</ul>'''),
        ('find-it-with-quick-open', 'Find it with Quick Open', '''<p>Press Control-Space to search your whole library.</p>
<ul>
<li>Type words from a name, keyword, URL, or folder. Press ↑ or ↓, then press Return.</li>
<li>Type or paste a web address to open it. You can also add it to your library.</li>
<li>Press Tab, or right-click a result, to use it another way. You can open it, copy its link, path, or command, or, for an app, show it in Finder.</li>
<li>Press ⌘1 through ⌘9 to open one of the first nine results.</li>
</ul>'''),
        ('keep-what-you-copy', 'Keep what you copy', '''<p>Library remembers what you copy. That includes text, links, images, and files, in the formats you copied them in.</p>
<ul>
<li>Open the <strong>Library</strong> menu or Quick Open to see your latest copies. Choose one to copy it again.</li>
<li>Pin an item to keep it after you quit.</li>
<li>Press Control-Command-V to open the clipboard menu at the pointer. Press 1 through 9 to copy an item. Hold Option to copy it as plain text.</li>
<li>If a text field has the keyboard, choosing an item pastes it. Otherwise it copies. To turn this off, use <strong>Paste into text fields</strong> in <strong>Settings &gt; Clipboard</strong>. Pasting needs Accessibility access.</li>
<li>Select an item in Quick Open and press Space to preview it in Quick Look.</li>
<li>When you copy a link, Library removes tracking codes such as <code>utm_source</code>, <code>fbclid</code>, and <code>gclid</code>. Turn this off in <strong>Settings &gt; General</strong>. Your history keeps the original link.</li>
<li>Copy as lower or upper case, trimmed, with its lines joined, or with smart punctuation. You can also copy a bookmark as a Markdown link. Find these in Quick Open, under Tab.</li>
<li>Library also finds addresses, phone numbers, and dates in copied text. See <a href="/smart-features/">smart features</a>.</li>
<li>Type <code>from Safari</code> in Quick Open to see only what you copied in Safari.</li>
<li>Build a paste queue. Add several items, then paste them one at a time, in order.</li>
<li>Library keeps the 50 most recent unpinned copies, up to 200 MB. Pinned items stay.</li>
<li>Lock pinned items with <strong>Require Touch ID or password to show pinned items</strong> in <strong>Settings &gt; Clipboard</strong>. <strong>Lock Pinned Items</strong> in the Library menu hides them again.</li>
</ul>
<p>Library skips anything a password manager marks as private. It also skips copies over 25 MB.</p>'''),
        ('save-snippets', 'Save snippets', '''<p>Save text you type often, such as an address or a standard reply, as a snippet. To add one, choose <strong>File &gt; New Snippet…</strong>, or click <strong>Snippets</strong> in the Library window.</p>
<p>To copy a snippet, type its name or a keyword in Quick Open, then press Return.</p>'''),
        ('organize-your-library', 'Organize your library', '''<p>Choose <strong>Edit Library…</strong> to manage everything in one window.</p>
<ul>
<li>Add items with the <strong>+</strong> menu. You can also drag an app or a link into the window.</li>
<li>Drag rows to reorder them, or to move them into a folder.</li>
<li>Select several rows to move, reorder, or edit them together. A bulk change is one undo step.</li>
<li>Deleted items go to <strong>Recently Deleted</strong>. They are removed for good after 30 days.</li>
<li>Right-click a row to open, edit or rename, move, share, or delete it. An app can also be shown in Finder.</li>
<li>To merge duplicate bookmarks, choose <strong>File &gt; Find Duplicates…</strong>.</li>
<li>To import bookmarks from Safari or Chrome, choose <strong>File &gt; Import Bookmarks…</strong>. They go into one folder. Press ⌘Z to undo the import.</li>
<li>To export or restore your whole library, use <strong>Settings &gt; General</strong>.</li>
</ul>
<p>Press ⌘Z to undo and ⇧⌘Z to redo.</p>'''),
        ('edit-an-item', 'Edit an item', '''<p>Select an item and press ⌘I. You can also choose <strong>Edit…</strong> from the toolbar or a right-click menu.</p>
<ul>
<li><strong>Name and icon.</strong> Pick an SF Symbol or an emoji, or keep the site's favicon or the app's icon.</li>
<li><strong>URL or Terminal Command</strong>, how a click opens it, and which browser to use.</li>
<li><strong>Keywords</strong> help Quick Open and Spotlight find the item.</li>
<li><strong>Color</strong> adds a dot in the menu and the Library window.</li>
<li><strong>Shortcuts</strong> can be added to any item.</li>
<li><strong>Open When You Log In</strong> opens the item a few seconds after you log in.</li>
</ul>'''),
        ('add-notes', 'Add notes', '''<p>Write a note on any item in Get Info. Quick Open shows the note under the item's name. Spotlight includes it in the description. Notes are plain text and stay in your library.</p>'''),
        ('use-templates', 'Use templates', '''<p>Put <code>{}</code> in a URL where a value goes. Library asks for the value when you open the bookmark.</p>
<p>To name several values, use <code>{project}</code> or <code>{id:Issue number}</code>. Library asks for all of them in one sheet.</p>'''),
        ('read-later', 'Read later', '''<p>Add a bookmark to the Reading List from its right-click menu, or press Tab in Quick Open.</p>
<ul>
<li>The list appears in the Library window and in the menu. Unread bookmarks show first.</li>
<li>Mark a bookmark as read or unread, or remove it from the list.</li>
<li>Removing a bookmark from the list keeps it in your library.</li>
</ul>'''),
        ('shortcuts', 'Shortcuts', '''<p>A shortcut can be a key combination, a modified click, a scroll, a pinch, a swipe, or a hot corner. Shortcut keys need Control, Option, or Command. An item can have several shortcuts.</p>
<p>The default shortcuts are Control and right-click for the menu, Control-Space for Quick Open, and Control-Command-V for the clipboard menu. To change them, use <strong>Settings &gt; Shortcuts</strong>.</p>'''),
        ('work-with-other-apps', 'Work with other apps', '''<ul>
<li><strong>Spotlight</strong> finds your bookmarks, apps, and commands.</li>
<li><strong>Services:</strong> select a link in any app, then choose <strong>Services &gt; Add to Library</strong>. In Finder, select apps or folders and choose the same item.</li>
<li><strong>Share:</strong> right-click a bookmark or app and choose <strong>Share…</strong>. Drag a row into any app to drop its link or file.</li>
<li><strong>URL scheme:</strong> <code>library://open?name=Jira&amp;value=ABC-123</code> opens a bookmark and fills in its template. <code>library://menu</code> shows the menu. <code>library://search</code> opens Quick Open. Terminal commands can't be opened this way, so a web page can't run one.</li>
<li><strong>Shortcuts app:</strong> actions for opening and searching items, adding bookmarks and apps, Frequently Used, and the clipboard. Run Terminal Command always asks first. These actions appear only in a build that includes App Intents metadata, which Xcode generates. A build from <code>./build.sh</code> does not show them yet.</li>
</ul>'''),
        ('stay-up-to-date', 'Stay up to date', '''<p>While Library runs, it checks GitHub for a new release every hour. It also checks at launch if the last check was an hour or more ago.</p>
<p>When a newer version exists, one item appears at the top of the menu. Nothing pops up. To turn checks off, use <strong>Settings &gt; General</strong>. Choose <strong>Check for Updates…</strong> at any time. It offers the newer version. If you choose to install it, Library opens Terminal, clones the release, and runs its installer. It does not install silently. See <a href="/privacy/#what-is-sent">what is sent</a>.</p>'''),
        ('settings', 'Settings', '''<p>Press ⌘, to open Settings.</p>
<ul>
<li><strong>General:</strong> startup, iCloud Drive, automatic update checks, link checks, names for new bookmarks, backup and restore, and link cleaning.</li>
<li><strong>Shortcuts:</strong> the global keys for the menu, Quick Open, the clipboard, and Open Copied Link.</li>
<li><strong>Clipboard:</strong> history, keeping history across restarts, pasting, GIFs, and the Touch ID or password lock for pinned items.</li>
</ul>'''),
        ('permissions', 'Permissions', '''<ul>
<li>Keyboard shortcuts, hot corners, Quick Open, and the menus don't need any permission.</li>
<li>Click, scroll, pinch, and swipe shortcuts, pasting into text fields, and suggesting a selected link need Accessibility access. Turn it on in <strong>System Settings &gt; Privacy &amp; Security &gt; Accessibility</strong>. Library reads your selection only when you open one of its menus, and it doesn't keep it.</li>
</ul>'''),
        ('troubleshooting', 'Troubleshooting', '''<ul>
<li><strong>A shortcut doesn't work.</strong> Another app may use the same keys. Check <strong>Settings &gt; Shortcuts</strong>. Control-Space can conflict with the macOS input source shortcut.</li>
<li><strong>Clicks stop working after a macOS update.</strong> Remove Library from Accessibility, then add it again.</li>
<li><strong>Open at Login does nothing.</strong> Move <code>Library.app</code> to <code>/Applications</code> first. The login item remembers where the app is.</li>
<li><strong>Services don't appear.</strong> Log out and back in, or run <code>/System/Library/CoreServices/pbs -update</code>.</li>
</ul>'''),
    ]
    out['/guide/index.html'] = page('/guide/', 'Library guide: features, settings, and permissions', 'Every feature, setting, and permission in Library.',
                                    'Every feature, setting, and permission in Library, with the steps to use each one.',
                                    guide_toc, guide)

    # ---------- Privacy ----------
    privacy_toc = [('what-is-stored', 'What is stored'), ('your-files', 'Your files'), ('what-is-sent', 'What is sent'),
                   ('touch-id-lock', 'Touch ID or password lock'), ('icloud-drive', 'iCloud Drive')]
    privacy = [
        ('what-is-stored', 'What is stored', '''<p>Library keeps your library and clipboard history on your Mac. Unpinned clipboard history stays in memory and is cleared when you quit, unless you turn on <strong>Keep clipboard history across restarts</strong> in <strong>Settings &gt; Clipboard</strong>. Only pinned items survive a quit otherwise.</p>
<p>Clipboard history never leaves your Mac.</p>'''),
        ('your-files', 'Your files', '''<p>Your files are in <code>~/.library/</code>:</p>
<table>
<caption>Files in ~/.library</caption>
<thead><tr><th scope="col">File</th><th scope="col">Contents</th></tr></thead>
<tbody>
<tr><th scope="row"><code>bookmarks.json</code></th><td>Your items, folders, shortcuts, and order</td></tr>
<tr><th scope="row"><code>clipboard.json</code></th><td>Pinned clipboard items, encrypted with a key kept in your Keychain</td></tr>
<tr><th scope="row"><code>clipboard-history.json</code></th><td>Unpinned clipboard history, encrypted the same way. This file exists only when <strong>Keep clipboard history across restarts</strong> is on. It is off by default.</td></tr>
<tr><th scope="row"><code>bookmarks-before-iCloud.json</code>, <code>bookmarks-iCloud-replaced.json</code></th><td>Backups kept when <strong>Keep Library in iCloud Drive</strong> is turned on, so no library is lost.</td></tr>
<tr><th scope="row"><code>bookmarks-damaged.json</code>, <code>snippets-damaged.json</code></th><td>A copy of a file that could not be read. Library tells you when it launches.</td></tr>
<tr><th scope="row"><code>snippets.json</code></th><td>Your snippets, as plain text. They are not encrypted, so don't keep passwords in a snippet.</td></tr>
<tr><th scope="row"><code>favicons/</code></th><td>Cached site icons. Library downloads them again if you delete the folder.</td></tr>
</tbody>
</table>
<p>Updates don't change your data.</p>'''),
        ('what-is-sent', 'What is sent', '''<p>Library connects to the internet only for these things.</p>
<ul>
<li><strong>Favicons</strong> (site icons) for the sites you bookmark.</li>
<li><strong>Copied GIFs</strong>, only if you turn on <strong>Play Copied GIFs</strong> in <strong>Settings &gt; Clipboard</strong>. It is off by default. Library downloads a GIF you copied from a web page so it can play.</li>
<li><strong>Link checks</strong>, only if you turn on <strong>Check links periodically</strong> in <strong>Settings &gt; General</strong>. It is off by default. Once a day, Library quickly checks that each bookmark's page is still there. It doesn't download the page. If a site doesn't answer that check, Library loads the page and reads only its first 64 KB.</li>
<li><strong>Smart titles</strong>, only if you turn on <strong>Name new bookmarks from their pages</strong> in <strong>Settings &gt; General</strong>. Library requests each new bookmark's page once and reads only the start of it to find the title.</li>
<li><strong>Update checks</strong> to <code>https://api.github.com/repos/deansasek/library/releases/latest</code>. This happens when you choose <strong>Check for Updates…</strong>, every hour while Library runs when automatic checks are on (the default), and at launch when the last check was an hour or more ago. The request names only the app's version, in its User-Agent header, and the ETag from GitHub's last answer. No account or other data is sent.</li>
<li><strong>Update in Terminal</strong>, only when you choose it. The release is cloned from <code>https://github.com/deansasek/library.git</code> into a temporary folder, which is deleted afterward.</li>
</ul>'''),
        ('touch-id-lock', 'Touch ID or password lock', '''<p>To lock pinned items, turn on <strong>Require Touch ID or password to show pinned items</strong> in <strong>Settings &gt; Clipboard</strong>. It is off by default.</p>
<p>Pinned items stay hidden until you authenticate. The unlock lasts until you choose <strong>Lock Pinned Items</strong>, your Mac sleeps, or Library quits. Search doesn't look inside locked items. If your Mac has no password or Touch ID, Library won't turn the lock on, and it explains how to add one.</p>'''),
        ('icloud-drive', 'iCloud Drive', '''<p>To keep your library in iCloud Drive, turn on <strong>Keep Library in iCloud Drive</strong> in <strong>Settings &gt; General</strong>. It is off by default.</p>
<p>Library moves <code>bookmarks.json</code> into the <code>Library</code> folder of iCloud Drive (<code>~/Library/Mobile Documents/com~apple~CloudDocs/Library/</code>) and links to it from <code>~/.library</code>. Your library then follows you to your other Macs. Clipboard history never leaves your Mac.</p>
<p>If two Macs change the library at the same time, the newer change wins for each item. Library tells you when a change from another Mac replaced an edit you hadn't saved.</p>
<h3>Temporary files</h3>
<p>Some files are written briefly to the system's temporary folder and then removed. A copy of a clip is written while you preview it in Quick Look. A terminal command is written as a script that deletes itself when Terminal runs it. A calendar event is written as an <code>.ics</code> file for Calendar. <strong>Export</strong> writes a backup file to the place you choose. It does not include clipboard items.</p>'''),
    ]
    out['/privacy/index.html'] = page('/privacy/', 'Privacy in Library: what is stored and sent', 'What Library stores, where it stores it, and what it sends over the network.',
                                      'What Library stores, where it stores it, and what it sends over the network.',
                                      privacy_toc, privacy)

    # ---------- Install ----------
    install_toc = [('requirements', 'Requirements'), ('install', 'Install'), ('first-steps', 'First steps'),
                   ('updates', 'Updates'), ('uninstall', 'Uninstall')]
    install = [
        ('requirements', 'Requirements', '''<dl class="requirements">
<div><dt>Operating system</dt><dd>macOS 26 or later</dd></div>
<div><dt>Developer tools</dt><dd>Xcode Command Line Tools</dd></div>
</dl>'''),
        ('install', 'Install', '''<p>Paste this into Terminal. It builds Library, puts <code>Library.app</code> in your Applications folder, and keeps the source code out of the way in Application Support.</p>
<div class="code-block"><pre><code>git clone https://github.com/deansasek/library.git "$HOME/Library/Application Support/Library/Source" &amp;&amp; "$HOME/Library/Application Support/Library/Source/install.sh"</code></pre></div>'''),
        ('first-steps', 'First steps', '''<ol>
<li>Press Control-Space to open Quick Open. Type a name and press Return.</li>
<li>Choose <strong>Edit Library…</strong> from the menu bar icon to add bookmarks and apps.</li>
<li>Turn on <strong>Open at Login</strong> in <strong>Settings &gt; General</strong> to start Library when your Mac starts.</li>
</ol>'''),
        ('updates', 'Updates', '''<p>Library checks for updates itself. <strong>Check for Updates…</strong> offers a newer version. If you choose to install it, Library opens Terminal, clones the release, and runs its installer. It does not install silently. Your library and pinned clipboard items are kept.</p>
<p>To update a clone made with the command above, run <code>update.sh</code> in the Source folder.</p>
<p>To learn how often Library checks, read <a href="/guide/#stay-up-to-date">Stay up to date</a>.</p>'''),
        ('uninstall', 'Uninstall', '''<ol>
<li>Quit Library.</li>
<li>Move <code>Library.app</code> from your Applications folder to the Trash.</li>
<li>Move the <strong>Library</strong> folder in <code>~/Library/Application Support</code> to the Trash. It holds the source you cloned.</li>
</ol>
<p>Your library and clipboard history stay in <code>~/.library</code>. Removing the app doesn't remove that folder. Move it to the Trash too if you want to delete your data.</p>'''),
    ]
    out['/install/index.html'] = page('/install/', 'Install Library on macOS with one command', 'Requirements, the one-command install, updates, and how to uninstall Library.',
                                      'Install Library with one command in Terminal. Requires macOS 26 or later.',
                                      install_toc, install)

    # ---------- Development ----------
    dev_toc = [('build', 'Build'), ('test', 'Test'), ('releasing', 'Releasing'), ('languages', 'Languages')]
    dev = [
        ('build', 'Build', '''<p>Run <code>./build.sh</code> to build the app.</p>
<p>On GitHub Actions, a pull request that changes code runs <code>./test.sh</code>. A push to <code>main</code> also builds the app and renders the screens. Changes to Markdown and <code>docs/</code> skip the run.</p>'''),
        ('test', 'Test', '''<p>Run <code>./test.sh</code> to run the checks in <code>Tests/</code>. The checks use private pasteboards and temporary files. They never touch your clipboard or your library.</p>'''),
        ('releasing', 'Releasing', '''<p>To publish a release, push a tag such as <code>vX.Y.Z</code>:</p>
<div class="code-block"><pre><code>git tag vX.Y.Z
git push origin vX.Y.Z</code></pre></div>
<p>Or run the <strong>Release</strong> workflow by hand and enter a version. Either way, GitHub Actions builds and checks the app, then publishes <code>Library-X.Y.Z.zip</code>. The zip holds only the source needed to build the app. Tests, workflows, docs, scripts, <code>test.sh</code>, and <code>update.sh</code> are left out.</p>
<p>If publishing fails with a server error, the workflow makes up to four attempts. Running it again is safe. It skips a release that already exists.</p>'''),
        ('languages', 'Languages', '''<p>Library is in English. The text lives in <code>Sources/Library/Resources/en.lproj/Localizable.strings</code>.</p>
<p>Write each user-facing string as <code>Text("…", bundle: L10n.bundle)</code>, or as <code>String(localized: "…", bundle: L10n.bundle)</code> where a <code>String</code> is needed. To add a string, add a line such as <code>"key" = "value";</code> with a <code>/* comment */</code> above it.</p>
<p>Dynamic text, such as file names, counts, and clipboard contents, isn't localized.</p>'''),
    ]
    out['/development/index.html'] = page('/development/', 'Building, testing, and releasing Library', 'Build, test, and release Library, and add languages.',
                                          'How to build, test, and release Library, and how text is localized.',
                                          dev_toc, dev)

    # ---------- Smart features ----------
    smart_toc = [('smart-actions', 'Smart actions'), ('smart-punctuation', 'Smart Punctuation'),
                 ('smart-titles', 'Smart titles'), ('smart-sorting', 'Smart sorting')]
    smart = [
        ('smart-actions', 'Smart actions', '''<p>If text has an address, a phone number, or a date, Library offers actions for it. Press Tab in Quick Open to see them: <strong>Open in Maps</strong>, <strong>Copy Phone Number</strong>, or <strong>Add to Calendar</strong>. Detection happens on your Mac.</p>'''),
        ('smart-punctuation', 'Smart Punctuation', '''<p>In <strong>Copy as</strong>, Smart Punctuation turns straight quotes and dashes into curly quotes, apostrophes, em dashes, and ellipses.</p>'''),
        ('smart-titles', 'Smart titles', '''<p>Turn on <strong>Name new bookmarks from their pages</strong> in <strong>Settings &gt; General</strong>. It is off by default. A new bookmark then takes the title of its page.</p>
<p>Library reads only the start of the page, and it requests each new bookmark's page once.</p>'''),
        ('smart-sorting', 'Smart sorting', '''<p>In the Edit Library window, open the sort menu in the header. Choose <strong>Most Used</strong> or <strong>Recently Opened</strong>.</p>'''),
    ]
    out['/smart-features/index.html'] = page('/smart-features/', 'Smart actions and smart titles in Library', 'Smart actions, Smart Punctuation, smart titles, and smart sorting in Library.',
                                             'Library works out what you copied and what you are doing. The next step is one choice away.',
                                             smart_toc, smart)

    # ---------- Releases ----------
    # No version or date here: the links always show the current release on GitHub.
    out['/releases/index.html'] = page('/releases/', 'Library releases: latest version and downloads', 'Download and read the notes for every Library release on GitHub.',
        'Release notes and downloads for every version of Library are on GitHub.',
        [], [], plain=True, extra=(
            '<ul class="links">'
            '<li><a href="https://github.com/deansasek/library/releases/latest" rel="noopener noreferrer">Get the Latest Release</a></li>'
            '<li><a href="https://github.com/deansasek/library/releases" rel="noopener noreferrer">See All Releases</a></li>'
            '</ul>'))

    # ---------- Accessibility ----------
    acc_toc = [('vision-and-motion', 'Motion and contrast'), ('keyboard', 'Keyboard'), ('voiceover', 'VoiceOver')]
    acc = [
        ('keyboard', 'Keyboard', """<p>Library works from the keyboard.</p>
<ul>
<li><strong>Control-Space</strong> opens Quick Open. Type to search, press <strong>↑</strong> or <strong>↓</strong> to move, and press <strong>Return</strong> to open the result. See <a href="/guide/#find-it-with-quick-open">Find it with Quick Open</a>.</li>
<li><strong>Tab</strong> opens a result the other way, or shows its other options.</li>
<li><strong>Space</strong> previews the selected item in Quick Look.</li>
<li><strong>Escape</strong> closes Quick Open.</li>
<li>In dialogs and sheets, <strong>Return</strong> confirms the default button, and <strong>Escape</strong> cancels.</li>
</ul>
<p>You can change the global keys in <a href="/guide/#shortcuts">Shortcuts</a>.</p>"""),
        ('voiceover', 'VoiceOver', """<p>Main controls have VoiceOver labels. Examples include <strong>Search Library</strong> in Quick Open, <strong>Actions</strong>, <strong>Sort</strong>, <strong>Add</strong>, <strong>Share</strong>, <strong>Delete</strong>, and <strong>Get Info</strong> in Edit Library.</p>
<p>Warnings about shortcuts that another app uses are labeled too.</p>
<p>To organize your library, see <a href="/guide/#organize-your-library">Organize your library</a>.</p>"""),
        ('report', 'Report a problem', """<p>If something in Library is hard to use with VoiceOver, the keyboard, or these settings, open an issue on the <a href="https://github.com/deansasek/library/issues" rel="noopener noreferrer">GitHub issues page</a>.</p>"""),
        ('vision-and-motion', 'Motion and contrast', """<ul>
<li><strong>Reduce Motion.</strong> When Reduce Motion is on, Quick Open's appearance animation is turned off. The Welcome screen does not animate between pages either.</li>
<li><strong>Increase Contrast.</strong> Quick Open uses system colors, which adapt to light and dark appearance and to Increase Contrast.</li>
</ul>
<p>Turn these on in <strong>System Settings</strong>. Library follows them.</p>"""),
    ]
    out['/accessibility/index.html'] = page('/accessibility/', 'Accessibility in Library: VoiceOver, keyboard, and motion',
        'How Library works with VoiceOver, the keyboard, Reduce Motion, and Increase Contrast.',
        'Library supports VoiceOver, keyboard use, Reduce Motion, and Increase Contrast. This page lists what the app does.',
        acc_toc, acc)

    # ---------- What's new ----------
    # Major and minor feature releases only. Data lives in content/whats_new.py.
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location('whats_new', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'whats_new.py'))
    _wn = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_wn)
    entries = ''
    for i, r in enumerate(_wn.RELEASES):
        badge = '<span class="badge">Latest</span>' if i == 0 else ''
        entries += (f'<section class="release"><h2><a href="/whats-new/{r["id"]}/">Library {r["version"]}</a></h2>'
                    f'<p class="updated">{r["date"]} {badge}</p><p>{r["summary"]}</p></section>')
    if not _wn.RELEASES:
        entries = '<p>No release notes yet.</p>'
    out['/whats-new/index.html'] = page('/whats-new/', "What's new in Library: release notes",
        'What each major and minor release of Library brings, newest first.',
        "What each major and minor release of Library brings, newest first.",
        [], [], plain=True, extra=entries + '<p class="links"><a href="https://github.com/deansasek/library/releases" rel="noopener noreferrer">See all releases on GitHub</a></p>')
    for r in _wn.RELEASES:
        out['/whats-new/' + r['id'] + '/index.html'] = release_page(page, r)

    # ---------- 404 ----------
    out['/404.html'] = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                        '<title>Page not found</title>\n<meta name="description" content="This page does not exist in Library.">\n'
                        '<meta name="robots" content="noindex">\n<link rel="canonical" href="https://getlibrary.app/404.html">\n<meta property="og:title" content="Page not found">\n<meta property="og:url" content="https://getlibrary.app/404.html">\n<meta property="og:description" content="This page does not exist in Library.">\n<meta property="og:image" content="https://getlibrary.app/assets/icon.png">\n<meta property="og:image:alt" content="Library app icon">\n<meta name="twitter:card" content="summary">\n<link rel="icon" type="image/png" sizes="256x256" href="/assets/icon.png">\n'
                        '<link rel="stylesheet" href="/styles.css">\n</head>\n<body>\n'
                        '<a class="skip-link" href="#main">Skip to content</a>\n'
                        + '__HEADER__' + '\n<main id="main" class="notfound"><h1>Page not found</h1>'
                        '<p class="subhead">This page doesn\'t exist.</p>'
                        '<p class="actions"><a class="button" href="/">Back to Library</a></p></main>\n'
                        + '__FOOTER__' + '\n</body>\n</html>\n')
    return out
