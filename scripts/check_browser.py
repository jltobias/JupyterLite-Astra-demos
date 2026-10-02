"""Smoke-test the built World Lab using a temporary localhost server.

Use --channel msedge or --channel chrome to use an installed browser.
Screenshots are saved in ignored test-results/ for visual review.
"""
import argparse
import functools
import http.server
from pathlib import Path
import threading
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',default='_build/html')
    parser.add_argument('--channel',default=None)
    parser.add_argument('--base-url',default='/')
    args=parser.parse_args()
    prefix='/' + args.base_url.strip('/') if args.base_url.strip('/') else ''
    site=Path(args.root).resolve()
    if not (site/'demos/index.html').is_file():
        raise SystemExit('Build and copy site assets first.')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if prefix and self.path.startswith(prefix+'/'):
                self.path=self.path[len(prefix):]
            super().do_GET()
        def log_message(self,*args):
            pass

    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(site)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}{prefix}'
    screenshots=ROOT/'test-results';screenshots.mkdir(exist_ok=True)
    errors=[];external=[];failed=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel=args.channel,headless=True,args=['--enable-unsafe-swiftshader'])
            page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:external.append(request.url) if urlparse(request.url).hostname not in ['127.0.0.1',None] else None)
            page.on('response',lambda response:failed.append(f'{response.status} {response.url}') if response.status>=400 else None)
            for name in ['terrain','city','globe','ocean','voxel','chaos']:
                page.goto(f'{base}/demos/?scene={name}',wait_until='networkidle')
                page.wait_for_function("document.querySelector('#metric').textContent.length > 0")
                assert page.locator('#fallback').is_hidden(),f'WebGL failed for {name}'
                assert page.locator(f'[data-scene="{name}"]').get_attribute('aria-pressed')=='true'
                assert page.locator('#play').get_attribute('aria-pressed')=='false'
                canvas=page.locator('#world')
                before=canvas.screenshot()
                canvas.focus();page.keyboard.press('ArrowLeft')
                assert before!=canvas.screenshot(),f'Orbit did not change {name}'
                page.locator('#reset').click()
                for control in ['primary','secondary']:
                    for endpoint in ['min','max']:
                        old=canvas.screenshot()
                        page.locator('#'+control).evaluate('(el, endpoint) => { el.value=el[endpoint]; el.dispatchEvent(new Event("input", {bubbles:true})); }',endpoint)
                        page.wait_for_timeout(180)
                        # Speed affects time evolution, not the paused t=0 wave surface.
                        if name=='ocean' and control=='secondary':
                            page.locator('#play').click();page.wait_for_timeout(250)
                            page.locator('#play').click()
                        assert old!=canvas.screenshot(),f'{name} {control} {endpoint} did not alter rendering'
                # Restore defaults before taking the publication review screenshot.
                page.locator(f'[data-scene="{name}"]').click()
                if name in ['globe','ocean','chaos']:
                    old=canvas.screenshot();page.locator('#play').click();page.wait_for_timeout(350)
                    assert old!=canvas.screenshot(),f'Motion did not change {name}'
                    page.locator('#play').click()
                href=page.locator('#lesson').get_attribute('href')
                notebook=href.split('path=')[1]
                assert (site/'lite/files'/notebook).is_file(),f'Notebook launch target missing: {notebook}'
                page.screenshot(path=str(screenshots/f'{name}-desktop.png'),full_page=True)
                print(f'PASS World Lab: {name}',flush=True)
            assert not errors,errors
            assert not failed,failed
            assert not external,f'World Lab made external requests: {external}'
            page.set_viewport_size({'width':390,'height':844})
            page.goto(f'{base}/demos/?scene=city',wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow on narrow screen'
            page.screenshot(path=str(screenshots/'city-mobile.png'),full_page=True)
            page.locator('#primary').focus();page.keyboard.press('ArrowRight')
            assert page.locator('#primary-value').inner_text()!='1×'
            # Ensure static fallback remains useful on browsers without WebGL.
            fallback=browser.new_page()
            fallback.add_init_script("const original=HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext=function(kind,...args){return kind.includes('webgl')?null:original.call(this,kind,...args)};")
            fallback.goto(f'{base}/demos/',wait_until='networkidle')
            assert fallback.locator('#fallback').is_visible()
            assert fallback.locator('#fallback a').get_attribute('href').endswith('00_start_here.ipynb')
            browser.close()
        print('PASS narrow layout, keyboard controls, no-WebGL fallback, local-only scene requests.')
    finally:
        server.shutdown();server.server_close()


if __name__=='__main__':
    main()
