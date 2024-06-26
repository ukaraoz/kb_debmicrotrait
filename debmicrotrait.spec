/*
A KBase module: debmicrotrait
*/

module debmicrotrait {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_debmicrotrait(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef run_deb(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
