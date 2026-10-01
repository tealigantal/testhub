#import <UIKit/UIKit.h>
#import <WebKit/WebKit.h>

@interface ZYGameViewController : UIViewController
@end

@implementation ZYGameViewController
- (BOOL)prefersStatusBarHidden { return YES; }
- (UIInterfaceOrientationMask)supportedInterfaceOrientations {
    return UIInterfaceOrientationMaskLandscape;
}
- (UIInterfaceOrientation)preferredInterfaceOrientationForPresentation {
    return UIInterfaceOrientationLandscapeRight;
}
- (BOOL)shouldAutorotate { return YES; }
@end

@interface ZYAppDelegate : UIResponder <UIApplicationDelegate, WKUIDelegate, WKNavigationDelegate>
@property(nonatomic,strong) UIWindow *window;
@property(nonatomic,strong) WKWebView *webView;
@end

@implementation ZYAppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];

    ZYGameViewController *vc = [ZYGameViewController new];
    vc.view.backgroundColor = [UIColor colorWithRed:0.03 green:0.08 blue:0.08 alpha:1.0];

    WKWebViewConfiguration *config = [WKWebViewConfiguration new];
    config.websiteDataStore = [WKWebsiteDataStore defaultDataStore];
    config.preferences.javaScriptEnabled = YES;
    config.preferences.javaScriptCanOpenWindowsAutomatically = YES;

    self.webView = [[WKWebView alloc] initWithFrame:vc.view.bounds configuration:config];
    self.webView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    self.webView.UIDelegate = self;
    self.webView.navigationDelegate = self;
    self.webView.backgroundColor = vc.view.backgroundColor;
    self.webView.opaque = NO;
    self.webView.scrollView.bounces = NO;
    self.webView.allowsBackForwardNavigationGestures = NO;

    if (@available(iOS 16.4, *)) {
        self.webView.inspectable = YES;
    }

    [vc.view addSubview:self.webView];
    self.window.rootViewController = vc;
    [self.window makeKeyAndVisible];

    NSURL *www = [[NSBundle mainBundle] URLForResource:@"www" withExtension:nil];
    NSURL *index = [www URLByAppendingPathComponent:@"index.html"];
    if (www && index) {
        [self.webView loadFileURL:index allowingReadAccessToURL:www];
    } else {
        NSString *html = @"<html><meta name='viewport' content='width=device-width'><body style='background:#071414;color:#eee;font-family:-apple-system;padding:2rem'><h2>照夜长生</h2><p>游戏资源缺失：www/index.html</p></body></html>";
        [self.webView loadHTMLString:html baseURL:nil];
    }
    return YES;
}

- (void)applicationDidEnterBackground:(UIApplication *)application {
    [self.webView evaluateJavaScript:@"try{window.dispatchEvent(new Event('pagehide'));document.dispatchEvent(new Event('visibilitychange'));}catch(e){}" completionHandler:nil];
}

- (void)applicationWillEnterForeground:(UIApplication *)application {
    [self.webView evaluateJavaScript:@"try{window.dispatchEvent(new Event('pageshow'));document.dispatchEvent(new Event('visibilitychange'));}catch(e){}" completionHandler:nil];
}

- (void)webView:(WKWebView *)webView
runJavaScriptAlertPanelWithMessage:(NSString *)message
initiatedByFrame:(WKFrameInfo *)frame
completionHandler:(void (^)(void))completionHandler {
    UIViewController *vc = self.window.rootViewController;
    UIAlertController *a = [UIAlertController alertControllerWithTitle:@"照夜长生" message:message preferredStyle:UIAlertControllerStyleAlert];
    [a addAction:[UIAlertAction actionWithTitle:@"确定" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action){ completionHandler(); }]];
    [vc presentViewController:a animated:YES completion:nil];
}

- (void)webView:(WKWebView *)webView
runJavaScriptConfirmPanelWithMessage:(NSString *)message
initiatedByFrame:(WKFrameInfo *)frame
completionHandler:(void (^)(BOOL result))completionHandler {
    UIViewController *vc = self.window.rootViewController;
    UIAlertController *a = [UIAlertController alertControllerWithTitle:@"照夜长生" message:message preferredStyle:UIAlertControllerStyleAlert];
    [a addAction:[UIAlertAction actionWithTitle:@"取消" style:UIAlertActionStyleCancel handler:^(__unused UIAlertAction *action){ completionHandler(NO); }]];
    [a addAction:[UIAlertAction actionWithTitle:@"确定" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action){ completionHandler(YES); }]];
    [vc presentViewController:a animated:YES completion:nil];
}

- (void)webView:(WKWebView *)webView
runJavaScriptTextInputPanelWithPrompt:(NSString *)prompt
defaultText:(NSString *)defaultText
initiatedByFrame:(WKFrameInfo *)frame
completionHandler:(void (^)(NSString * _Nullable result))completionHandler {
    UIViewController *vc = self.window.rootViewController;
    UIAlertController *a = [UIAlertController alertControllerWithTitle:@"照夜长生" message:prompt preferredStyle:UIAlertControllerStyleAlert];
    [a addTextFieldWithConfigurationHandler:^(UITextField *field){ field.text = defaultText ?: @""; }];
    [a addAction:[UIAlertAction actionWithTitle:@"取消" style:UIAlertActionStyleCancel handler:^(__unused UIAlertAction *action){ completionHandler(nil); }]];
    [a addAction:[UIAlertAction actionWithTitle:@"确定" style:UIAlertActionStyleDefault handler:^(__unused UIAlertAction *action){ completionHandler(a.textFields.firstObject.text ?: @""); }]];
    [vc presentViewController:a animated:YES completion:nil];
}

@end

int main(int argc, char * argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass([ZYAppDelegate class]));
    }
}
