import re
import sublime
import sublime_plugin

ts_pattern = re.compile("^\s*(?:(\d*:)?(\d*:))?(\d*)(\.\d*)?\s*$")


def expand(view, point, selector):
    if not view.match_selector(point, selector):
        raise ValueError(
            "point %d does not match selector %s" % (point, selector))

    region = sublime.Region(point, point + 1)
    while region.a >= 0 and view.match_selector(region.a - 1, selector):
        region.a -= 1
    while view.match_selector(region.b, selector):
        region.b += 1

    return region


def has_sel(view, empty_means_yes):
    if len(view.sel()) == 0:
        return False
    if len(view.sel()) > 1:
        return True
    if not view.sel()[0].empty():
        return True
    return empty_means_yes == view.sel()[0].empty()


def ms_to_ts(ms):
    if ms < 0:
        ms = 0
    h = (ms / 1000 / 60 / 60)
    m = (ms / 1000 / 60) % 60
    s = (ms / 1000) % 60
    ms %= 1000

    if h >= 1:
        ts = "%02d:%02d:%02d.%03d" % (h, m, s, ms)
    else:
        ts = "%02d:%02d.%03d" % (m, s, ms)

    return ts


def run_for_selector(view, region, selector, callback, *args):
    # Better go backwards since region size may decrease
    point = region.end()
    while point >= region.begin():
        if view.match_selector(point, selector):
            target = expand(view, point, selector)
            callback(target, *args)
            point = target.a
        point -= 1


def ts_to_ms(ts):
    match = ts_pattern.match(ts)
    if not match:
        sublime.status_message("unexpected timestamp format")
        return

    ms = 0
    if match.group(1) and len(match.group(1)) > 1:
        ms += int(match.group(1)[:-1]) * 3600 * 1000
    if match.group(2) and len(match.group(2)) > 1:
        ms += int(match.group(2)[:-1]) * 60 * 1000
    if match.group(3):
        ms += int(match.group(3)) * 1000
    if match.group(4) and len(match.group(4)) > 1:
        ms += int(match.group(4)[1:])

    return ms


class WebvttApplyShift(sublime_plugin.TextCommand):
    def run(self, edit, offset):
        if has_sel(self.view, False):
            for region in self.view.sel():
                self.run_in_region(region, edit, offset)
        else:
            region = sublime.Region(0, self.view.size())
            self.run_in_region(region, edit, offset)

    def run_in_region(self, region, edit, offset):
        selector = "meta.timestamp.webvtt"
        run_for_selector(self.view, region, selector, self.shift, edit, offset)

    def shift(self, region, edit, offset):
        timestamp = self.view.substr(region)
        ms = ts_to_ms(timestamp)
        ms += offset
        timestamp = ms_to_ts(ms)
        self.view.replace(edit, region, str(timestamp))


class WebvttShift(sublime_plugin.WindowCommand):
    def on_done(self, text):
        if text[:1] == "-":
            offset = - ts_to_ms(text[1:])
        else:
            offset = ts_to_ms(text)
        if offset:
            view = self.window.active_view()
            view.run_command('webvtt_apply_shift', {'offset': offset})

    def run(self):
        self.window.show_input_panel("Shift by", "", self.on_done, None, None)
