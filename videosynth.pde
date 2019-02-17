import processing.sound.*;
import processing.video.*;
import milchreis.imageprocessing.*;
import beads.*;

// global constants
int NUM_VOICES = 3;
int TONIC = 69;
int SCALE[] = {0, 2, 4, 5, 7, 9, 11, 12};

int octave;

Capture mov;
PImage grad;

// oscillators
Glide freq[];
WavePlayer pwm_osc;
WavePlayer tri_osc;
WavePlayer oscs[][];

// filter parameters
OnePoleFilter filter;
Glide cutoff;

// audio context parameters
AudioContext ac;
Gain g;

int time_begin;

void captureEvent(Capture m)
{
  m.read(); 
}

void setup()
{
  // video setup
  size(640, 360);
  String[] cameras = Capture.list();
  for (int i = 0; i < cameras.length; i++) {
     println(cameras[i]); 
  }
  mov = new Capture(this, 320, 180, 30);
  mov.start();
  
  // sound setup
  ac = new AudioContext();
  
  g = new Gain(ac, 1, 0.5);
  
  cutoff = new Glide(ac, 1000.0, 50.0); // lpf cutoff freq  
  filter = new OnePoleFilter(ac, cutoff); //, 0.0);
  
  freq = new Glide[NUM_VOICES];
  
  // TODO: control volume of oscillators?

  oscs = new WavePlayer[NUM_VOICES][2];
  for (int i = 0; i < NUM_VOICES; i++) {
    freq[i] = new Glide(ac, 440.0, 50); // osc1 frequency
    oscs[i][0] = new WavePlayer(ac, freq[i], Buffer.SQUARE);
    oscs[i][1] = new WavePlayer(ac, freq[i], Buffer.TRIANGLE);
    filter.addInput(oscs[i][0]);
    filter.addInput(oscs[i][1]);
  }

  g.addInput(filter);
  ac.out.addInput(g);
  
  ac.start();
  time_begin = millis();
}

void draw()
{
  int time_end = millis();
  // compute image gradient
  grad = mov.copy();
  grad.resize(160,120);
  grad = SobelEdgeDetector.apply(grad);
  grad = grad.get(1, 1, 158, 118);  // remove gradient at border
  float grad_mean = img_mean(grad);
  image(grad, 0, 0, 640, 360);//, 0, 0, 1280, 720);
  fill(color(grad_mean));
  rect(0, 0, 20, 20);
  
  float filter_val = ((grad_mean / 255.0) * 10000.0);
  
  cutoff.setValue(filter_val);
  fill(#FFFFFF);

  if (time_end - time_begin > 4000) {
    time_begin = millis();
    float chord[] = gen_chord("rand", -1);
    play(chord);
  }

  text(filter_val, 0, 40);
  //text(freq.getValue(), 0, 60);
  //text(pwm_osc.getFrequency(), 0, 80);
  //filter.setFrequency(filter_val);
}

int img_mean(PImage img)
{
  PImage cpy = img.copy();
  cpy.filter(GRAY);
  int acc = 0;
  int dim = img.width * img.height;
  for (int i = 0; i < dim; i++) {
      acc += extract_channel(img.pixels[i], 0);
  }
  
  return acc / dim;
}

int extract_channel(color c, int channel)
{
  return (c >> (8 * channel)) & 0xFF;
}

float midi_to_hz(int note)
{
  return pow(2.0, (note - 69.0)/12.0) * 440.0; 
}

float[] gen_chord(String mode, int octave)
{
  float chord[] = new float[NUM_VOICES];
  
  if (mode == "rand") {
    for (int i = 0; i < NUM_VOICES; i++) {
      chord[i] = midi_to_hz((TONIC + (12 * octave)) + SCALE[int(random(0, 8))]);
    }
  } else {
    // not implemented 
  }
  
  return chord;
}

void play(float[] chord)
{
   for (int i = 0; i < NUM_VOICES; i++) {
     println(chord[i]);
     freq[i].setValue(chord[i]);
   }
}
