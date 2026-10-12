import brut.androlib.src.SmaliBuilder;
import brut.directory.ExtFile;
import java.io.File;

/** Smali folder -> classes.dex (apktool ke smali assembler se).
 *  Use: java -cp apktool.jar:. SmaliRun <smali_dir> <out.dex> <api_level> */
public class SmaliRun {
    public static void main(String[] a) throws Exception {
        SmaliBuilder.build(new ExtFile(new File(a[0])), new File(a[1]), Integer.parseInt(a[2]));
        System.out.println("dex written: " + a[1]);
    }
}
